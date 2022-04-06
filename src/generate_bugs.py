import argparse
import sys
import pathlib
import subprocess

import utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to generate bugs for all projects of a dataset")
    parser = utils.add_core_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = utils.load_dataset(args)

    if args.perturbation_model == None:
        print("The perturbation_model option must be set.")
        sys.exit(1)

    for bug in dataset.get_bugs():
        for file in pathlib.Path(bug.get_path()).glob("**/*.java"):
            # We don't want to generate bugs on the tests
            relative_path = str(file.relative_to(pathlib.Path(bug.get_path())))
            if "test" not in relative_path and "Test" not in relative_path:
                cmd = "timeout 600 java -jar %s %s" % (args.perturbation_model, file)
                run = subprocess.run(cmd, shell=True, capture_output=True)
                sys.exit(0)

        # TODO: debug purposes only
        break
