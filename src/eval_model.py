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


def identical(fixed_line, tentative_fix):
    return fixed_line.strip() == tentative_fix.strip() or \
            fixed_line.split() == tentative_fix.split() or \
            fixed_line.replace(" ", "") == tentative_fix.replace(" ", "")


def evaluate_fix(args, original_bug, fixed_line, tentative_fix):
    return identical(fixed_line, tentative_fix)


def evaluate(bugs):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained).to(device)
    
    results = {}
    for bug in bugs:
        bug_result = { "hunks" : {} }
        for hunk_id, hunk in enumerate(bugs[bug]):
            hunk_result = { "patches" : [] }

            max_input_length = 768
            source = tokenizer(hunk["source"], max_length=max_input_length, truncation=True, return_tensors='pt')
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
            for i, target in enumerate(target_ids):
                tentative_fix = tokenizer.decode(target, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                identical = evaluate_fix(args, bug, hunk["target"], tentative_fix)
                fix = {}
                fix["k"] = i+1
                fix["patch"] = tentative_fix
                fix["identical"] = identical
                hunk_result["patches"].append(fix)
                hunk_result["ground_truth"] = hunk["target"]

            bug_result["hunks"][hunk_id] = hunk_result
        results[bug] = bug_result
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to evaluate a pretrained model on a given dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_eval_args(parser)
    args = parser.parse_args()

    # Read the input json
    with open(pathlib.Path(args.storage, args.model_input), "r") as f:
        bugs = json.load(f)

    # Run the filter function in separate threads (one for each project)
    results = evaluate(bugs)

    with open(args.results_file, "w") as f:
        json.dump(results, f, indent=4)
