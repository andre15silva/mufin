import numpy as np
import argparse
import pathlib
import os
import tempfile
import uuid
import json
from unidiff import PatchSet

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


def apply_fix(original_bug, tentative_fix):
    # Parse the diff and access info
    diff = PatchSet(original_bug.get_diff())
    original_file = diff[0].source_file

    # Read the lines of the original file
    with open(original_file, "r") as f:
        lines = f.readlines()

    # Replace the lines by the tentative_fix
    target_start = diff[0][0].target_start
    target_length = diff[0][0].target_length
    lines[target_start - 1] = tentative_fix + "\n"
    lines = lines[:target_start] + lines[target_start + target_length - 1:]

    # Write content to a temporary file
    fixed_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False, suffix=".java")
    fixed_file.writelines(lines)
    fixed_file.flush()
    fixed_file.close()

    # Compute diff
    diff = utils.get_diff(original_file, fixed_file.name)
    os.remove(str(pathlib.Path(fixed_file.name).absolute()))

    return diff


# TODO: implement this as the definitive version
def preprocess_buggy_to_fixed(tokenizer, bug):
    source = model_utils.source_str(bug.get_diff())
    target = model_utils.target_str(bug.get_diff())

    # TODO: parametrize this
    max_input_length = 732
    return tokenizer(source, max_length=max_input_length, truncation=True, return_tensors='pt'), target


# TODO: implement this as the definitive version
def preprocess_fixed_to_buggy(tokenizer, bug):
    pass


def evaluate_fix(args, original_bug, tentative_fix):
    try:
        # 1 - Checkout the buggy version
        original_bug.checkout()

        # 2 - Create the bug fix
        diff = apply_fix(original_bug, tentative_fix)
        print(diff)
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


# TODO: implement this
def evaluate_bug(bug, tentative_bug):
    print("generated " + tentative_bug)
    return True


def evaluate(args):
    dataset = serialization_utils.load_dataset(args)

    tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained)
    
    results = {}
    for bug in dataset.get_bugs():
        # TODO: Choose according to parameter
        source, target = preprocess_buggy_to_fixed(tokenizer, bug)
        
        # TODO: parametrize this
        target_ids = model.generate(
                input_ids=source.input_ids,
                attention_mask=source.attention_mask,
                num_beams=50,
                max_length=732,
                early_stopping=True,
                )

        # Generate the tentative solution
        tentative_fix = tokenizer.decode(target_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)

        # TODO: Choose according to parameter
        diff, comp, test = evaluate_fix(args, bug, tentative_fix)
        bug_result = {}
        bug_result["patch"] = tentative_fix
        bug_result["patch_diff"] = diff
        bug_result["comp_execute"] = comp.is_executing()
        bug_result["comp_pass"] = comp.is_passing()
        bug_result["test_execute"] = test.is_executing()
        bug_result["test_pass"] = test.is_passing()
        results[bug.get_identifier()] = bug_result

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to evaluate a pretrained model on a given dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_eval_args(parser)
    args = parser.parse_args()

    results = evaluate(args)

    with open(args.results_file, "w") as f:
        json.dump(results, f)
