import argparse
import sys
from joblib import Parallel, delayed

import utils
import serialization_utils


def filter_function(bugs):
    to_remove = set()
    for bug in bugs:
        # Check bugs and fixed versions
        comp_bug = bug.compile()
        comp_fixed = bug.compile_fixed()
        if not comp_bug.is_executing() or \
            not comp_bug.is_passing() or \
            not comp_fixed.is_executing() or \
            not comp_fixed.is_passing():
            print("Bug %s failed to compile." % bug.get_identifier())
            to_remove.add(bug)
    return to_remove


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs that do not compile.")
    parser = utils.add_core_args(parser)
    parser = utils.add_filtering_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = serialization_utils.load_dataset(args)

    # Separate the bugs by project
    projects = {}
    for bug in dataset.get_bugs():
        if bug.get_path() in projects:
            projects[bug.get_path()] = projects[bug.get_path()].append(bug)
        else:
            projects[bug.get_path()] = [bug]

    # Run the filter function in separate threads (one for each project)
    results = Parallel(n_jobs=8)(delayed(filter_function)(project) for project in projects.values())

    # Flatten the results
    to_remove = set()
    for result in results:
        to_remove.update(result)

    # Remove bugs that don't compile
    for bug in to_remove:
        dataset.get_bugs().remove(bug)

    print("\n\nRemoved %d bugs that don't compile." % len(to_remove))

    # Save the metadata
    serialization_utils.save_dataset(args, dataset)
