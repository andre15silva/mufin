import argparse
import sys

import utils

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
        if not comp:
            print("Bug %s tests didn't run." % bug.get_identifier())
            to_remove.add(bug)

    # Remove bugs that don't compile
    for bug in to_remove:
        #dataset.get_bugs().remove(bug)
        pass

    print("\n\nRemoved %d bugs whose tests don't run." % len(to_remove))

    # Save the metadata
    utils.save_dataset(args, dataset)
