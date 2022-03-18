import argparse
import sys

import utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs with non-single file patches.")
    parser = utils.add_core_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = utils.load_dataset(args)

    # Print stats
    print("Identifier: " + dataset.get_identifier())
    print("Number of bugs: " + len(dataset.get_bugs()))
