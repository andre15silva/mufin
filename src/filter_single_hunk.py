import argparse
import sys
from unidiff import PatchSet

import utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs with non-single hunk patches.")
    parser = utils.add_core_args(parser)
    parser = utils.add_filtering_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = utils.load_dataset(args)

    # Check bugs patches
    to_remove = set()
    for bug in dataset.get_bugs():
        diff = PatchSet(bug.get_diff())
        if args.ignore_empty_diff and len(diff) == 0:
            print("Bug %s has %d files associated to its patch, but it will be included." % (bug.get_identifier(), len(diff)))
        elif len(diff) != 1:
            print("Bug %s has %d files associated to its patch." % (bug.get_identifier(), len(diff)))
            to_remove.add(bug)
        elif diff[0].is_added_file or diff[0].is_removed_file:
            print("There was some error with bug %s since it consideres it a new file or removed file." % bug.get_identifier())
        elif len(diff[0]) != 1:
            print("Bug %s has %d hunks associated with its single-file patch." % (bug.get_identifier(), len(diff[0])))
            to_remove.add(bug)
        elif args.keep_single_line_only and diff[0][0].added != 1 and diff[0][0].removed != 1:
            print("Bug %s is not single line" % bug.get_identifier())
            to_remove.add(bug)


    # Remove non single-file diffs
    for bug in to_remove:
        dataset.get_bugs().remove(bug)

    print("\n\nRemoved %d bugs with non single-hunk patches." % len(to_remove))

    # Save the metadata
    utils.save_dataset(args, dataset)
