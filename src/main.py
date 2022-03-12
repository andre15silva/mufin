import argparse
import pickle
from pathlib import Path

from defects4j import Defects4J

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to checkout all bugs (buggy and fixed versions) from Defects4J")
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    parser.add_argument("--defects4j", help="Path to the defects4j directory", required=False, metavar="<path_to_defects4j>")
    args = parser.parse_args()

    if args.defects4j != None:
        defects4j = None
        if Path(args.storage, "defects4j.pickle").exists():
            with open(Path(args.storage, "defects4j.pickle").absolute(), "rb") as f:
                defects4j = pickle.load(f)
        else:
            defects4j = Defects4J(Path(args.defects4j).absolute())

        defects4j.checkout_all(Path(args.storage).absolute())
        print(defects4j.check_integrity(Path(args.storage).absolute()))

        with open(Path(args.storage, "defects4j.pickle").absolute(), "wb") as f:
            pickle.dump(defects4j, f)
