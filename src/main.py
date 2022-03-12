import argparse
import pickle
from pathlib import Path

from defects4j import Defects4J
from bugsdotjar import BugsDotJar
from bears import Bears

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to checkout all bugs (buggy and fixed versions) from Defects4J")
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    parser.add_argument("--defects4j", help="Path to the defects4j directory", required=False, metavar="<path_to_defects4j>")
    parser.add_argument("--bugs-dot-jar", help="Path to the Bugs.jar directory", required=False, metavar="<path_to_bears>")
    parser.add_argument("--bears", help="Path to the bears directory", required=False, metavar="<path_to_bears>")
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

        # TODO: do stuff

        with open(Path(args.storage, "defects4j.pickle").absolute(), "wb") as f:
            pickle.dump(defects4j, f)

    if args.bugs_dot_jar != None:
        bugs_dot_jar = None
        if Path(args.storage, "bugs_dot_jar.pickle").exists():
            with open(Path(args.storage, "bugs_dot_jar.pickle").absolute(), "rb") as f:
                bugs_dot_jar = pickle.load(f)
        else:
            bugs_dot_jar = BugsDotJar(Path(args.bugs_dot_jar).absolute())
            bugs_dot_jar.checkout_all(Path(args.storage).absolute())
            print(bugs_dot_jar.check_integrity(Path(args.storage).absolute()))

        # TODO: do stuff

        with open(Path(args.storage, "bugs_dot_jar.pickle").absolute(), "wb") as f:
            pickle.dump(bugs_dot_jar, f)

    if args.bears != None:
        bears = None
        if Path(args.storage, "bears.pickle").exists():
            with open(Path(args.storage, "bears.pickle").absolute(), "rb") as f:
                bears = pickle.load(f)
        else:
            bears = Bears(Path(args.bears).absolute())
            bears.checkout_all(Path(args.storage).absolute())
            print(bears.check_integrity(Path(args.storage).absolute()))

        # TODO: do stuff

        with open(Path(args.storage, "bears.pickle").absolute(), "wb") as f:
            pickle.dump(bears, f)
