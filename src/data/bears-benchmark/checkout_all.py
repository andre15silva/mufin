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
    if bugs is not None:
        for bug in bugs:
            bug_id = bug["bugId"]
            bug_branch = bug["bugBranch"]

            buggy_path = os.path.abspath(os.path.join(args.storage, bug_id, "buggy"))
            if not os.path.exists(buggy_path):
                os.makedirs(buggy_path)
            else:
                continue
            fixed_path = os.path.abspath(os.path.join(args.storage, bug_id, "fixed"))
            if not os.path.exists(fixed_path):
                os.makedirs(fixed_path)
            else:
                continue

            # check out the branch containing the bug
            cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout %s;" % (bears_path, bug_branch)
            subprocess.call(cmd, shell=True)

            # copy all files to the fixed folder
            cmd = "cd %s; cp -r . %s;" % (bears_path, fixed_path)
            subprocess.call(cmd, shell=True)

            # check out buggy commit from the branch containing the bug
            cmd = "cd %s; git log --format=format:%%H --grep='Changes in the tests';" % bears_path
            buggy_commit = subprocess.check_output(cmd, shell=True).decode("utf-8")
            if len(buggy_commit) == 0:
                cmd = "cd %s; git log --format=format:%%H --grep='Bug commit';" % bears_path
                buggy_commit = subprocess.check_output(cmd, shell=True).decode("utf-8")

            cmd = "cd %s; git checkout %s;" % (bears_path, buggy_commit)
            subprocess.call(cmd, shell=True)

            # copy all files to the bug folder
            cmd = "cd %s; cp -r . %s;" % (bears_path, buggy_path)
            subprocess.call(cmd, shell=True)

            # check out master
            cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout master;" % bears_path
            subprocess.call(cmd, shell=True)
