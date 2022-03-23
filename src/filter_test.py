import argparse
import sys

import utils

from models.test_result import TestResult

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs whose tests don't run.")
    parser = utils.add_core_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = utils.load_dataset(args)

    # Check bugs patches
    to_remove = set()
    for bug in dataset.get_bugs():
        comp = bug.test()
        if not comp.is_executes():
            print("Bug %s tests didn't execute." % bug.get_identifier())
            to_remove.add(bug)

    # Remove bugs that don't compile
    for bug in to_remove:
        dataset.get_bugs().remove(bug)

    print("\n\nRemoved %d bugs whose tests didn't execute." % len(to_remove))

    # Save the metadata
    utils.save_dataset(args, dataset)
