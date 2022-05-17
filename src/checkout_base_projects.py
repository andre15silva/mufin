import argparse
import pathlib
import sys

import utils
import serialization_utils

from models.defects4j.defects4j import Defects4J
from models.bugsdotjar.bugsdotjar import BugsDotJar
from models.bears.bears import Bears
from models.quixbugs.quixbugs import QuixBugs

def checkout_dataset(args):
    if args.defects4j != None:
        defects4j = Defects4J(pathlib.Path(args.defects4j).absolute())
        defects4j.checkout_oldests(pathlib.Path(args.storage).absolute())
        return defects4j

    elif args.bugsdotjar != None:
        bugsdotjar = BugsDotJar(pathlib.Path(args.bugsdotjar).absolute())
        bugsdotjar.checkout_oldests(pathlib.Path(args.storage).absolute())
        return bugsdotjar

    elif args.bears != None:
        bears = Bears(pathlib.Path(args.bears).absolute())
        bears.checkout_oldests(pathlib.Path(args.storage).absolute())
        return bears

    elif args.quixbugs != None:
        quixbugs = QuixBugs(pathlib.Path(args.quixbugs).absolute())
        quixbugs.checkout_oldests(pathlib.Path(args.storage).absolute())
        return quixbugs
    
    else:
        return NotImplementedError("%s" % args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to checkout the oldest fixed version of each project contained in the dataset.")
    parser = utils.add_core_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = checkout_dataset(args)

    # Check its integrity
    if not dataset.check_oldests(pathlib.Path(args.storage)):
        raise Exception("Dataset integrity check failed")

    # Save the metadata
    serialization_utils.save_dataset(args, dataset)
