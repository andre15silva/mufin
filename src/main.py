import argparse
import pickle
import json
from pathlib import Path

from defects4j.defects4j import Defects4J
from bugsdotjar.bugsdotjar import BugsDotJar
from bears.bears import Bears
from quixbugs.quixbugs import QuixBugs

from serialization.encoders import BugEncoder, DatasetEncoder
from serialization.decoders import DatasetDecoder

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to checkout all bugs (buggy and fixed versions) from Defects4J")
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    parser.add_argument("--defects4j", help="Path to the defects4j directory", required=False, metavar="<path_to_defects4j>")
    parser.add_argument("--bugsdotjar", help="Path to the Bugs.jar directory", required=False, metavar="<path_to_bears>")
    parser.add_argument("--bears", help="Path to the bears directory", required=False, metavar="<path_to_bears>")
    parser.add_argument("--quixbugs", help="Path to the QuixBugs directory", required=False, metavar="<path_to_quixbugs>")
    args = parser.parse_args()

    if args.defects4j != None:
        defects4j = None
        if Path(args.storage, "defects4j.json").exists():
            with open(Path(args.storage, "defects4j.json").absolute(), "r") as f:
                defects4j = json.load(f, cls=DatasetDecoder)
        else:
            defects4j = Defects4J(Path(args.defects4j).absolute())
            defects4j.checkout_all(Path(args.storage).absolute())

        print(defects4j.check_integrity(Path(args.storage).absolute()))
        print(len(defects4j.get_bugs()))

        with open(Path(args.storage, "defects4j.json").absolute(), "w+") as f:
            json.dump(defects4j, f, cls=DatasetEncoder)

    if args.bugsdotjar != None:
        bugsdotjar = None
        if Path(args.storage, "bugsdotjar.json").exists():
            with open(Path(args.storage, "bugsdotjar.json").absolute(), "r") as f:
                bugsdotjar = json.load(f, cls=DatasetDecoder)
        else:
            bugsdotjar = BugsDotJar(Path(args.bugsdotjar).absolute())
            bugsdotjar.checkout_all(Path(args.storage).absolute())

        print(bugsdotjar.check_integrity(Path(args.storage).absolute()))
        print(len(bugsdotjar.get_bugs()))

        with open(Path(args.storage, "bugsdotjar.json").absolute(), "w+") as f:
            json.dump(bugsdotjar, f, cls=DatasetEncoder)

    if args.bears != None:
        bears = None
        if Path(args.storage, "bears.json").exists():
            with open(Path(args.storage, "bears.json").absolute(), "r") as f:
                bears = json.load(f, cls=DatasetDecoder)
        else:
            bears = Bears(Path(args.bears).absolute())
            bears.checkout_all(Path(args.storage).absolute())

        print(bears.check_integrity(Path(args.storage).absolute()))
        print(len(bears.get_bugs()))

        with open(Path(args.storage, "bears.json").absolute(), "w+") as f:
            json.dump(bears, f, cls=DatasetEncoder)

    if args.quixbugs != None:
        quixbugs = None
        if Path(args.storage, "quixbugs.json").exists():
            with open(Path(args.storage, "quixbugs.json").absolute(), "r") as f:
                quixbugs = json.load(f, cls=DatasetDecoder)
        else:
            quixbugs = QuixBugs(Path(args.quixbugs).absolute())
            quixbugs.checkout_all(Path(args.storage).absolute())

        print(quixbugs.check_integrity(Path(args.storage).absolute()))
        print(len(quixbugs.get_bugs()))

        with open(Path(args.storage, "quixbugs.json").absolute(), "w+") as f:
            json.dump(quixbugs, f, cls=DatasetEncoder)
