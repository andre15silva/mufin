import argparse
import sys

import utils

from models.test_result import TestResult

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs whose tests don't run properly.")
    parser = utils.add_core_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = utils.load_dataset(args)

    # Check bugs patches
    to_remove = set()
    for bug in dataset.get_bugs():
        test_bug = bug.test()
        test_fixed = bug.test_fixed()
        if not test_fixed.is_executing() or not test_fixed.is_executing():
            print("Bug %s tests didn't execute." % bug.get_identifier())
            to_remove.add(bug)
        elif test_bug.is_passing():
            print("Bug %s is buggy but the tests pass." % bug.get_identifier())
            to_remove.add(bug)
        elif not test_fixed.is_passing():
            print("Bug %s is fixed but the tests fail." % bug.get_identifier())
            to_remove.add(bug)

    # Remove bugs that don't execute the tests
    for bug in to_remove:
        dataset.get_bugs().remove(bug)

    print("\n\nRemoved %d bugs whose tests didn't execute properly." % len(to_remove))

    # Save the metadata
    utils.save_dataset(args, dataset)
