import argparse
import sys
from joblib import Parallel, delayed
from unidiff import PatchSet

import utils
import serialization_utils


def filter_function(bugs):
    # Check bugs patches
    to_remove = set()
    for bug in bugs:
        diff = PatchSet(bug.get_diff())
        if args.ignore_empty_diff and len(diff) == 0:
            print("Bug %s has %d files associated to its patch, but it will be included." % (bug.get_identifier(), len(diff)))
        elif len(diff) != 1:
            print("Bug %s has %d files associated to its patch." % (bug.get_identifier(), len(diff)))
            to_remove.add(bug)
        elif diff[0].is_added_file or diff[0].is_removed_file:
            print("There was some error with bug %s since it consideres it a new file or removed file." % bug.get_identifier())
            to_remove.add(bug)
        elif len(diff[0]) != 1:
            print("Bug %s has %d hunks associated with its single-file patch." % (bug.get_identifier(), len(diff[0])))
            to_remove.add(bug)
        elif args.keep_single_line_only and diff[0][0].added != 1 and diff[0][0].removed != 1 and not( \
                [line.target_line_no for line in diff[0][0].target_lines() if line.is_added][0] != None and \
                [line.source_line_no for line in diff[0][0].source_lines() if line.is_removed][0] != None and \
                [line.target_line_no for line in diff[0][0].target_lines() if line.is_added][0] == \
                [line.source_line_no for line in diff[0][0].source_lines() if line.is_removed][0]):
            print("Bug %s is not single line" % bug.get_identifier())
            to_remove.add(bug)
    return to_remove


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs with non-single hunk patches.")
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

    # Remove non single-file diffs
    for bug in to_remove:
        dataset.get_bugs().remove(bug)

    print("\n\nRemoved %d bugs with non single-hunk patches." % len(to_remove))

    # Save the metadata
    serialization_utils.save_dataset(args, dataset)
