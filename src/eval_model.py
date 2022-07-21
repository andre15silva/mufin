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


def extract_ground_truth(bug):
    # Parse the diff and access info
    diff = PatchSet(bug.get_diff())
    
    start_buggy = -1
    end_buggy = -1
    for i, line in enumerate(diff[0][0].target_lines()):
        if line.is_added:
            if start_buggy == -1:
                start_buggy = i
            if end_buggy < i:
                end_buggy = i
    start_fix = -1
    end_fix = -1
    for i, line in enumerate(diff[0][0].source_lines()):
        if line.is_removed:
            if start_fix == -1:
                start_fix = i
            if end_fix < i:
                end_fix = i
    
    buggy_line = ""
    for i, line in enumerate(diff[0][0].target_lines()):
        if i >= start_buggy and i <= end_buggy:
            buggy_line += " " + line.value.strip() + " "

    fixed_line = ""
    for i, line in enumerate(diff[0][0].source_lines()):
        if i >= start_fix and i <= end_fix:
            fixed_line += " " + line.value.strip() + " "

    return " ".join(buggy_line.split()), " ".join(fixed_line.split())


def apply_fix(original_bug, tentative_fix):
    # Parse the diff and access info
    diff = PatchSet(original_bug.get_diff())
    original_file = diff[0].source_file

    # Read the lines of the original file
    with open(original_file, "r") as f:
        lines = f.readlines()

    start_buggy = -1
    start_buggy_ln = -1
    end_buggy = -1
    end_buggy_ln = -1
    for i, line in enumerate(diff[0][0].target_lines()):
        if line.is_added:
            if start_buggy == -1:
                start_buggy = i
                start_buggy_ln = line.target_line_no
            if end_buggy < i:
                end_buggy = i
                end_buggy_ln = line.target_line_no
    if start_buggy_ln == -1 or end_buggy_ln == -1:
        return None

    # Replace the lines by the tentative_fix
    lines = lines[:start_buggy_ln-1] + [tentative_fix + "\n"] + lines[end_buggy_ln:]
    print(tentative_fix)

    # Write content to a temporary file
    fixed_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False, suffix=".java")
    fixed_file.writelines(lines)
    fixed_file.flush()
    fixed_file.close()

    # Compute diff
    diff = utils.get_diff(original_file, fixed_file.name)
    os.remove(str(pathlib.Path(fixed_file.name).absolute()))

    return diff


def preprocess_buggy_to_fixed(tokenizer, bug):
    source = model_utils.source_str(bug.get_diff())
    target = model_utils.target_str(bug.get_diff())

    max_input_length = 732
    return tokenizer(source, max_length=max_input_length, truncation=True, return_tensors='pt'), target


def evaluate_fix(args, original_bug, tentative_fix):
    try:
        # 1 - Checkout the buggy version
        original_bug.checkout()

        # 2 - Create the bug fix
        diff = apply_fix(original_bug, tentative_fix)
        if diff == None:
            original_bug.restore()
            raise Exception("Bug %s is not patchable..." % original_bug.get_identifier())
        bug_fix = create_bug(args, original_bug, diff)

        # 3 - Test the bug fix
        comp = bug_fix.compile()
        test = bug_fix.test()

        # 4 - Revert to the fixed version
        original_bug.restore()

        return diff, comp, test
    except Exception as e:
        print(e)
        return tentative_fix, CompileResult(False, False), TestResult(False, False)


def evaluate(bugs):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained).to(device)
    
    results = {}
    for bug in bugs:
        source, target = preprocess_buggy_to_fixed(tokenizer, bug)
        source = source.to(device)
        
        target_ids = model.generate(
                input_ids=source.input_ids,
                attention_mask=source.attention_mask,
                num_beams=args.beam_width,
                max_length=128,
                early_stopping=False,
                num_return_sequences=args.beam_width,
                )

        # Generate the tentative solution
        bug_result = { "fixes" : [] }
        buggy_line, fixed_line = extract_ground_truth(bug)
        bug_result["buggy_line"] = buggy_line
        bug_result["fixed_line"] = fixed_line
        for i, target in enumerate(target_ids):
            tentative_fix = tokenizer.decode(target, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            diff, comp, test = evaluate_fix(args, bug, tentative_fix)
            fix = {}
            fix["k"] = i+1
            fix["patch"] = tentative_fix
            fix["patch_diff"] = diff
            fix["comp_execute"] = comp.is_executing()
            fix["comp_pass"] = comp.is_passing()
            fix["test_execute"] = test.is_executing()
            fix["test_pass"] = test.is_passing()
            bug_result["fixes"].append(fix)

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
    results = Parallel(n_jobs=8)(delayed(evaluate)(project) for project in projects.values())

    # Merge results
    merged_results = {}
    for result in results:
        for bug in result:
            merged_results[bug] = result[bug]

    with open(args.results_file, "w") as f:
        json.dump(merged_results, f, indent=4)
