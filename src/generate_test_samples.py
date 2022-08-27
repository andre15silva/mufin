import argparse
import sys
import pathlib
import subprocess
import os
import json
from unidiff import PatchSet

import utils
import model_utils
import serialization_utils


def get_target_idxs(hunk):
    targets = []

    last_target_line_no = -1
    start_line = -1
    found_added = False
    start_buggy = -1
    end_buggy = -1
    for i, line in enumerate(hunk):
        if not line.is_removed:
            last_target_line_no = line.target_line_no
        if line.is_added or line.is_removed:
            if start_buggy == -1:
                start_buggy = i
                start_line = last_target_line_no
            if end_buggy < i:
                end_buggy = i
            if line.is_added and not found_added:
                found_added = True
                start_line = line.target_line_no
        elif start_buggy != -1 and end_buggy != -1:
            targets.append((start_buggy, end_buggy, start_line))
            start_buggy = -1
            start_line = -1
            found_added = False
            end_buggy = -1

    return targets


def get_context(args, bug, file, hunk, targets):
    try:
        # Checkout the buggy version
        bug.checkout()

        # Get the context
        cmd = "timeout 600 java -jar %s %s %s" % (args.perturbation_model, file, "test-" + str(targets[2]))
        run = subprocess.run(cmd, shell=True, capture_output=True)

        # Restore the fixed version
        bug.restore()
        
        return run.stdout.decode("utf-8").strip()
    except Exception as e:
        print(e)
        return ""


def get_src_tgt(hunk, targets, context):
    source = model_utils.source_str_hunk_targets(hunk, targets, context)
    target = model_utils.target_str_hunk_targets(hunk, targets)
    return source, target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to generate bugs test samples from a dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_generation_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = serialization_utils.load_dataset(args)

    bugs = {}
    for bug in dataset.get_bugs():

        # Parse the diff and access info
        diff = PatchSet(bug.get_diff())

        bug_hunks = []
        for file in diff:
            hunk_id = 0
            for hunk in file:
                target_idxs = get_target_idxs(hunk)
                for targets in target_idxs:
                    context = get_context(args, bug, file.source_file, hunk, targets)
                    source, target = get_src_tgt(hunk, targets, context)
                    bug_hunks += [{
                        "file" : file.source_file,
                        "hunk" : str(hunk),
                        "source" : source, 
                        "target" : target
                        }]
        
        bugs[bug.get_identifier()] = bug_hunks

    path = pathlib.Path(args.storage, args.model_output)
    with open(path, "w") as f:
        json.dump(bugs, f, indent=4)
