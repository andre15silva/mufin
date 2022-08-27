import numpy as np
import argparse
import pathlib
import os
import tempfile
import uuid
import json
import torch
from unidiff import PatchSet
from joblib import Parallel, delayed

from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, T5Config, Seq2SeqTrainingArguments, Seq2SeqTrainer

import utils
import model_utils
import serialization_utils
from models.compile_result import CompileResult
from models.test_result import TestResult
from models.bug import Bug
from models.defects4j.defects4jbug import Defects4JBug
from models.bugsdotjar.bugsdotjar import BugsDotJarBug
from models.bears.bearsbug import BearsBug
from models.quixbugs.quixbugsbug import QuixBugsBug


def create_bug(args, original_bug, diff) -> Bug:
    uid = str(uuid.uuid4())
    if args.defects4j != None:
        return Defects4JBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), diff)
    elif args.bugsdotjar != None:
        return BugsDotJarBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), diff)
    elif args.bears != None:
        return BearsBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), diff)
    elif args.quixbugs != None:
        return QuixBugsBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), diff)
    else:
        return NotImplementedError("%s" % args)


def extract_ground_truth(hunk, targets):
    source = model_utils.source_str_hunk_targets(hunk, targets, "")
    target = model_utils.target_str_hunk_targets(hunk, targets)

    source_split_start = source.split("[START_BUGGY]")[1]
    source_split_end = source_split_start.split("[END_BUGGY]")[0]

    return source_split_end.strip(), target.strip()


def apply_fix(original_bug, tentative_fix):
    # Parse the diff and access info
    diff = PatchSet(original_bug.get_diff())
    type_ = model_utils.get_type(original_bug.get_diff())
    original_file = diff[0].source_file

    # Read the lines of the original file
    with open(original_file, "r") as f:
        lines = f.readlines()

    if type_ == "REPLACE" or type_ == "REMOVE":
        start_buggy = -1
        start_buggy_ln = -1
        end_buggy = -1
        end_buggy_ln = -1
        for i, line in enumerate(diff[0][0]):
            if line.is_added:
                if start_buggy == -1:
                    start_buggy = i
                    start_buggy_ln = line.target_line_no
                if end_buggy < i:
                    end_buggy = i
                    end_buggy_ln = line.target_line_no

        lines = lines[:start_buggy_ln-1] + [tentative_fix + "\n"] + lines[end_buggy_ln:]

    elif type_ == "ADD":
        start_buggy = False
        start_buggy_ln = -1
        end_buggy = False
        end_buggy_ln = -1
        for i, line in enumerate(diff[0][0]):
            if line.is_removed:
                start_buggy = True
                end_buggy = True
            elif not start_buggy:
                start_buggy_ln = line.target_line_no
            elif end_buggy:
                end_buggy = False
                end_buggy_ln = line.target_line_no - 1

        # Add the lines
        lines = lines[:start_buggy_ln] + [tentative_fix + "\n"] + lines[end_buggy_ln:]

    # Write content to a temporary file
    fixed_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False, suffix=".java")
    fixed_file.writelines(lines)
    fixed_file.flush()
    fixed_file.close()

    # Compute diff
    diff = utils.get_diff(original_file, fixed_file.name)
    os.remove(str(pathlib.Path(fixed_file.name).absolute()))

    return diff


def preprocess_buggy_to_fixed(tokenizer, hunk, targets):
    # TODO: include context
    source = model_utils.source_str_hunk_targets(hunk, targets, "")
    target = model_utils.target_str_hunk_targets(hunk, targets)

    max_input_length = 768
    return tokenizer(source, max_length=max_input_length, truncation=True, return_tensors='pt'), target


def identical(fixed_line, tentative_fix):
    return fixed_line.strip() == tentative_fix.strip() or \
            fixed_line.split() == tentative_fix.split() or \
            fixed_line.replace(" ", "") == tentative_fix.replace(" ", "")


def evaluate_fix(args, original_bug, fixed_line, tentative_fix):
    if identical(fixed_line, tentative_fix):
        return "", True, CompileResult(True, True), TestResult(True, True)
    # TODO: Implement execution for perfect fault localization on several lines
    else:
        return "", False, CompileResult(False, False), TestResult(False, False)
#
#    try:
#        # 1 - Checkout the buggy version
#        original_bug.checkout()
#
#        # 2 - Create the bug fix
#        diff = apply_fix(original_bug, tentative_fix)
#        if diff == None:
#            original_bug.restore()
#            raise Exception("Bug %s is not patchable..." % original_bug.get_identifier())
#        bug_fix = create_bug(args, original_bug, diff)
#
#        # 3 - Test the bug fix
#        comp = bug_fix.compile()
#        test = bug_fix.test()
#
#        # 4 - Revert to the fixed version
#        original_bug.restore()
#
#        return diff, False, comp, test
#    except Exception as e:
#        print(e)
#        return tentative_fix, False, CompileResult(False, False), TestResult(False, False)


def get_target_idxs(hunk):
    targets = []

    start_buggy = -1
    end_buggy = -1
    for i, line in enumerate(hunk):
        if line.is_added or line.is_removed:
            if start_buggy == -1:
                start_buggy = i
            if end_buggy < i:
                end_buggy = i
        elif start_buggy != -1 and end_buggy != -1:
            targets.append((start_buggy, end_buggy))
            start_buggy = -1
            end_buggy = -1

    return targets


def evaluate(bugs):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained).to(device)
    
    results = {}
    for bug in bugs:
        # Parse the diff and access info
        diff = PatchSet(bug.get_diff())

        bug_result = { "files" : {} }
        for file in diff:
            file_result = {}
            hunk_id = 0
            for hunk in file:
                target_idxs = get_target_idxs(hunk)

                for targets in target_idxs:
                    hunk_result = { "patches" : [] }
                    source, target = preprocess_buggy_to_fixed(tokenizer, hunk, targets)
                    source = source.to(device)
                
                    target_ids = model.generate(
                            input_ids=source.input_ids,
                            attention_mask=source.attention_mask,
                            num_beams=args.beam_width,
                            max_length=128,
                            early_stopping=True,
                            num_return_sequences=args.beam_width,
                            )

                    # Generate the tentative solution
                    buggy_line, fixed_line = extract_ground_truth(hunk, targets)
                    hunk_result["buggy_line"] = buggy_line
                    hunk_result["fixed_line"] = fixed_line
                    for i, target in enumerate(target_ids):
                        tentative_fix = tokenizer.decode(target, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                        diff, identical, comp, test = evaluate_fix(args, bug, fixed_line, tentative_fix)
                        fix = {}
                        fix["k"] = i+1
                        fix["patch"] = tentative_fix
                        fix["patch_diff"] = diff
                        fix["identical"] = identical
                        fix["comp_execute"] = comp.is_executing()
                        fix["comp_pass"] = comp.is_passing()
                        fix["test_execute"] = test.is_executing()
                        fix["test_pass"] = test.is_passing()
                        hunk_result["patches"].append(fix)

                    file_result[hunk_id] = hunk_result
                    hunk_id += 1
            bug_result["files"][file.source_file] = file_result
        results[bug.get_identifier()] = bug_result
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to evaluate a pretrained model on a given dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_eval_args(parser)
    args = parser.parse_args()
    
    # Load the dataset
    dataset = serialization_utils.load_dataset(args)
    
    # Separate the bugs by project
    projects = {}
    for bug in dataset.get_bugs():
        if bug.get_path() in projects:
            projects[bug.get_path()].append(bug)
        else:
            projects[bug.get_path()] = [bug]

    # Run the filter function in separate threads (one for each project)
    results = Parallel(n_jobs=1)(delayed(evaluate)(project) for project in projects.values())

    # Merge results
    merged_results = {}
    for result in results:
        for bug in result:
            merged_results[bug] = result[bug]

    with open(args.results_file, "w") as f:
        json.dump(merged_results, f, indent=4)
