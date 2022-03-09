import argparse
from pathlib import Path

from defects4j import Defects4J

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to checkout all bugs (buggy and fixed versions) from Defects4J")
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    parser.add_argument("--defects4j", help="Path to the defects4j directory", required=True, metavar="<path_to_defects4j>")
    args = parser.parse_args()

    defects4j = Defects4J(Path(args.defects4j).absolute())
    defects4j.checkout_all(Path(args.storage).absolute())

    for bug in defects4j.get_bugs():
        print(bug)
        print(bug.compile())
        print(bug.test())
