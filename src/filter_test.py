import argparse
import sys
from joblib import Parallel, delayed

import utils
import serialization_utils

from models.test_result import TestResult


def filter_function(bugs):
    to_remove = set()
    for bug in bugs:
        # We only want to check the fixed version because it has no diff
        if not bug.get_diff():
            test_fixed = bug.test_fixed()
            if not test_fixed.is_executing() or not test_fixed.is_executing():
                print("Bug %s tests didn't execute." % bug.get_identifier())
                to_remove.add(bug)
        else:
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
    return to_remove


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs whose tests don't run properly.")
    parser = utils.add_core_args(parser)
    parser = utils.add_filtering_args(parser)
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
    results = Parallel(n_jobs=8)(delayed(filter_function)(project) for project in projects.values())

    # Flatten the results
    to_remove = set()
    for result in results:
        to_remove.update(result)

    # Remove bugs that don't execute the tests
    for bug in to_remove:
        dataset.get_bugs().remove(bug)

    print("\n\nRemoved %d bugs whose tests didn't execute properly." % len(to_remove))

    # Save the metadata
    serialization_utils.save_dataset(args, dataset)
