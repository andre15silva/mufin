import argparse
import subprocess
import os
import json
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to checkout all bugs (buggy and fixed versions) from Bugs.jar")
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    parser.add_argument("--bugs", help="Path to the Bugs.jar directory", required=True, metavar="<path_to_bears>")
    args = parser.parse_args()
    
    # Get all project ids
    bugs_path = os.path.abspath(args.bugs)

    # get all bugs
    bugs = None
    directories = [x for x in os.listdir(bugs_path) if os.path.isdir(os.path.join(bugs_path, x))]

    for project in directories:
        # get all bug branches
        project_path = os.path.join(bugs_path, project)
        cmd = "cd %s; git branch -a | grep \"bugs-dot-jar_\" ;" % project_path
        bug_branches = [x.decode("utf-8") for x in subprocess.check_output(cmd, shell = True).split()]

        for branch in bug_branches:
            # checkout buggy branch and copy to the bug folder
            bug = branch
            if "/" in branch: bug = branch.split("/")[2]
            if not bug.startswith("bugs-dot-jar_"): continue

            # copy to buggy path
            buggy_path = os.path.abspath(os.path.join(args.storage, bug, "buggy"))
            if not os.path.exists(buggy_path): os.makedirs(buggy_path)
            cmd = "cd %s; git checkout %s; cp -r . %s;" % (project_path, bug, buggy_path)
            subprocess.call(cmd, shell=True)

            # copy to fixed path
            fixed_path = os.path.abspath(os.path.join(args.storage, bug, "fixed"))
            if not os.path.exists(buggy_path): os.makedirs(buggy_path)
            cmd = "cd %s; git checkout %s; cp -r . %s;" % (project_path, bug, fixed_path)
            subprocess.call(cmd, shell=True)

            # apply patch in fixed version
            cmd = "cd %s; patch -p1 < .bugs-dot-jar/developer-patch.diff;" % fixed_path
            subprocess.call(cmd, shell=True)
