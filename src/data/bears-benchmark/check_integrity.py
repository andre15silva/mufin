import argparse
import subprocess
import os
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to checkout all bugs (buggy and fixed versions) from Bears")
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    parser.add_argument("--bears", help="Path to the bears directory", required=True, metavar="<path_to_bears>")
    args = parser.parse_args()
    
    # Get all project ids
    bears_path = os.path.abspath(args.bears)

    # check out master
    cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout master;" % bears_path
    subprocess.call(cmd, shell=True)

    # get all bugs
    bugs = None
    if os.path.exists(os.path.join(bears_path, "scripts/data/bug_id_and_branch.json")):
        with open(os.path.join(bears_path, "scripts/data/bug_id_and_branch.json"), 'r') as f:
            try:
                bugs = json.load(f)
            except Exception as e:
                print("got %s on json.load()" % e)
                sys.exit()

    # Checkout all buggy and fixed versions
    count = 0
    if bugs is not None:
        for bug in bugs:
            bug_id = bug["bugId"]
            bug_branch = bug["bugBranch"]
            count += 1

            buggy_path = os.path.abspath(os.path.join(args.storage, bug_id, "buggy", ".git"))
            fixed_path = os.path.abspath(os.path.join(args.storage, bug_id, "fixed", ".git"))
            if not os.path.exists(buggy_path) or not os.path.exists(fixed_path):
                missing.add(bug_id)

    if len(missing) > 0:
        print("There is/are " + str(len(missing)) + " bug(s) missing or with compromised integrity.")
        for bug in missing:
            print(bug)
        sys.exit(1)
    else:
        print("There are no bugs missing or with compromised integrity.")
        sys.exit(0)
