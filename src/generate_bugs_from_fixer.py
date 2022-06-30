import numpy as np
import pandas as pd
import argparse
import pathlib
import subprocess
import functools
import tempfile
import os
import uuid
import torch

from unidiff import PatchSet
from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, T5Config, Seq2SeqTrainingArguments, Seq2SeqTrainer

import utils
import serialization_utils
import model_utils
from models.compile_result import CompileResult
from models.test_result import TestResult
from models.bug import Bug
from models.defects4j.defects4jbug import Defects4JBug
from models.bugsdotjar.bugsdotjar import BugsDotJarBug
from models.bears.bearsbug import BearsBug
from models.quixbugs.quixbugsbug import QuixBugsBug


def create_bug(args, original_bug, diff, reverse_diff) -> Bug:
    uid = str(uuid.uuid4())
    if args.defects4j != None:
        return Defects4JBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), diff), Defects4JBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), reverse_diff)
    elif args.bugsdotjar != None:
        return BugsDotJarBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), diff), BugsDotJarBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), reverse_diff)
    elif args.bears != None:
        return BearsBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), diff), BearsBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), reverse_diff)
    elif args.quixbugs != None:
        return QuixBugsBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), diff), QuixBugsBug(original_bug.get_identifier() + "-tentative_fix-" + uid, original_bug.get_path(), reverse_diff)
    else:
        return NotImplementedError("%s" % args)


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
        return None, None

    # Replace the lines by the tentative_fix
    lines = lines[:start_buggy_ln-1] + [tentative_fix + "\n"] + lines[end_buggy_ln:]

    # Write content to a temporary file
    fixed_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False, suffix=".java")
    fixed_file.writelines(lines)
    fixed_file.flush()
    fixed_file.close()

    # Compute diff
    diff = utils.get_diff(original_file, fixed_file.name)
    reverse_diff = utils.get_diff(fixed_file.name, original_file)
    os.remove(str(pathlib.Path(fixed_file.name).absolute()))

    return diff, reverse_diff


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
        diff, reverse_diff = apply_fix(original_bug, tentative_fix)
        if diff == None or reverse_diff == None:
            original_bug.restore()
            raise Exception("Bug %s is not patchable..." % original_bug.get_identifier())
        bug_fix, reversed_bug_fix = create_bug(args, original_bug, diff, reverse_diff)

        # 3 - Test the bug fix
        comp = bug_fix.compile()
        test = bug_fix.test()

        # 4 - Revert to the fixed version
        original_bug.restore()

        # We return the reversed_bug_fix because our tokenization mechanisms need a diff that is applied to a fixed version
        return reversed_bug_fix, comp, test
    except Exception as e:
        print(e)
        return None, CompileResult(False, False), TestResult(False, False)


def generate(args):
    dataset = serialization_utils.load_dataset(args)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained).to(device)
    
    no_filter_dataset = serialization_utils.create_empty_dataset(args)
    filter_compile_dataset = serialization_utils.create_empty_dataset(args)
    filter_test_dataset = serialization_utils.create_empty_dataset(args)
    for bug in dataset.get_bugs():
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
        for i, target in enumerate(target_ids):
            tentative_fix = tokenizer.decode(target, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            new_bug, comp, test = evaluate_fix(args, bug, tentative_fix)
            if new_bug == None:
                continue

            no_filter_dataset.add_bug(new_bug)
            if comp.is_executing() and comp.is_passing():
                filter_compile_dataset.add_bug(new_bug)
            if test.is_executing() and test.is_passing():
                filter_test_dataset.add_bug(new_bug)

    # Save the datasets
    no_filter_path = pathlib.Path(args.storage, args.model_output.split(".json")[0] + "_hunk.json")
    serialization_utils.save_dataset_to_file(args, no_filter_dataset, no_filter_path)
    filter_compile_path = pathlib.Path(args.storage, args.model_output.split(".json")[0] + "_hunk_compile.json")
    serialization_utils.save_dataset_to_file(args, filter_compile_dataset, filter_compile_path)
    filter_test_path = pathlib.Path(args.storage, args.model_output.split(".json")[0] + "_hunk_compile_test.json")
    serialization_utils.save_dataset_to_file(args, filter_test_dataset, filter_test_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to generate a dataset with a pretrained model from a given dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_eval_args(parser)
    args = parser.parse_args()

    generate(args)
