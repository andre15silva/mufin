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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to generate bugs test samples from a dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_generation_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = serialization_utils.load_dataset(args)

    bugs = {}
    for bug in dataset.get_bugs():

        bugs[bug.get_identifier()] = {
                    "diff" : bug.get_diff(),
                    "source" : model_utils.source_str(bug.get_diff()),
                    "target" : model_utils.target_str(bug.get_diff())
                }
        #break

    path = pathlib.Path(args.storage, args.model_output)
    with open(path, "w") as f:
        json.dump(bugs, f, indent=4)
