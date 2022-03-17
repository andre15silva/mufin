import argparse
import sys
from unidiff import PatchSet

import utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs with non-single file patches.")
    parser = utils.add_core_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = utils.load_dataset(args)

    # Check bugs patches
    to_remove = set()
    for bug in dataset.get_bugs():
        n_files = len(PatchSet(bug.get_diff()))
        if n_files != 1:
            print("Bug %s has %d files associated to its patch." % (bug.get_identifier(), n_files))
            to_remove.add(bug)

    # Remove non single-file diffs
    for bug in to_remove:
        dataset.get_bugs().remove(bug)

    print("\n\nRemoved %d bugs with non single-file patches." % len(to_remove))

    # Save the metadata
    utils.save_dataset(args, dataset)
