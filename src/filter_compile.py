import argparse
import sys

import utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs that do not compile.")
    parser = utils.add_core_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = utils.load_dataset(args)

    # Check bugs patches
    to_remove = set()
    for bug in dataset.get_bugs():
        comp = bug.compile()
        if not comp:
            print("Bug %s failed to compile." % bug.get_identifier())
            to_remove.add(bug)

    # Remove bugs that don't compile
    for bug in to_remove:
        dataset.get_bugs().remove(bug)

    print("\n\nRemoved %d bugs that don't compile." % len(to_remove))

    # Save the metadata
    utils.save_dataset(args, dataset)
