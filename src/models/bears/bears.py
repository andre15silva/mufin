import pathlib
import subprocess
import json
import shutil
from datetime import datetime

import utils
from models.bug import Bug
from models.dataset import Dataset
from models.bears.bearsbug import BearsBug

class Bears(Dataset):
    
    def __init__(self, path: pathlib.Path) -> None:
        super().__init__("bears", path)

    
    def checkout_oldests(self, storage: pathlib.Path) -> None:
        # check out master
        cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout andre;" % self.path
        subprocess.call(cmd, shell=True)

        # get all bugs info and branches
        bugs_to_branches = None
        bugs = None
        with open(pathlib.Path(self.path, "scripts", "data", "bug_id_and_branch.json"), 'r') as f:
            bugs_to_branches = json.load(f)
            bugs_to_branches = {bug["bugId"] : bug["bugBranch"] for bug in bugs_to_branches}
        with open(pathlib.Path(self.path, "docs", "data", "bears-bugs.json"), "r") as f:
            bugs = json.load(f)

        # Find oldest version of each project
        oldests = {}
        if bugs is not None:
            for bug in bugs:
                project = bug["repository"]["name"]
                bug_id = bug["bugId"]
                date = bug["builds"]["fixerBuild"]["date"]
                date = datetime.strptime(date, "%b %d, %Y %I:%M:%S %p")

                if project not in oldests or oldests[project][1] > date:
                    oldests[project] = (bug_id, date)

        # Checkout the fixed version of the oldest versions of each project
        if bugs_to_branches is not None:
            for project in oldests:
                bug_id = oldests[project][0]
                bug_branch = bugs_to_branches[bug_id]

                fixed_path = pathlib.Path(storage, self.identifier, "%s" % bug_id).absolute()
                if not fixed_path.exists():
                    fixed_path.mkdir(parents=True)
                else:
                    continue

                # check out the branch containing the bug
                cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout %s;" % (self.path, bug_branch)
                subprocess.call(cmd, shell=True)

                # copy all files to the fixed folder
                cmd = "cd %s; cp -r . %s;" % (self.path, fixed_path)
                subprocess.call(cmd, shell=True)

                # check out master
                cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout andre;" % self.path
                subprocess.call(cmd, shell=True)

                # copy compilation and testing scripts
                cmd = "cd %s; cp compile_bug.py %s; cp run_tests_bug.py %s" % (pathlib.Path(self.path, "scripts"), fixed_path, fixed_path)
                subprocess.call(cmd, shell=True)

                # add bug
                self.add_bug(BearsBug(bug_id, fixed_path, ""))


    def check_oldests(self, storage: pathlib.Path) -> bool:
        # check out master
        cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout andre;" % self.path
        subprocess.call(cmd, shell=True)

        # get all bugs info and branches
        bugs_to_branches = None
        bugs = None
        with open(pathlib.Path(self.path, "scripts", "data", "bug_id_and_branch.json"), 'r') as f:
            bugs_to_branches = json.load(f)
            bugs_to_branches = {bug["bugId"] : bug["bugBranch"] for bug in bugs_to_branches}
        with open(pathlib.Path(self.path, "docs", "data", "bears-bugs.json"), "r") as f:
            bugs = json.load(f)

        # Find oldest version of each project
        oldests = {}
        if bugs is not None:
            for bug in bugs:
                project = bug["repository"]["name"]
                bug_id = bug["bugId"]
                date = bug["builds"]["fixerBuild"]["date"]
                date = datetime.strptime(date, "%b %d, %Y %I:%M:%S %p")

                if project not in oldests or oldests[project][1] > date:
                    oldests[project] = (bug_id, date)

        # Checkout the fixed version of the oldest versions of each project
        missing = set()
        if bugs_to_branches is not None:
            for project in oldests:
                bug_id = oldests[project][0]
                bug_branch = bugs_to_branches[bug_id]

                fixed_path = pathlib.Path(storage, self.identifier, "%s" % bug_id).absolute()
                if not fixed_path.exists():
                    missing.add(bug_id)

        return len(missing) == 0


    def checkout_all(self, storage: pathlib.Path) -> None:
        # check out master
        cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout andre;" % self.path
        subprocess.call(cmd, shell=True)

        # get all bugs
        bugs = None
        if pathlib.Path(self.path, "scripts/data/bug_id_and_branch.json").exists():
            with open(pathlib.Path(self.path, "scripts", "data", "bug_id_and_branch.json"), 'r') as f:
                bugs = json.load(f)

        # Checkout all buggy and fixed versions
        if bugs is not None:
            for bug in bugs:
                bug_id = bug["bugId"]
                bug_branch = bug["bugBranch"]

                buggy_path = pathlib.Path(storage, self.identifier, "%s-buggy" % bug_id).absolute()
                fixed_path = pathlib.Path(storage, self.identifier, "%s" % bug_id).absolute()
                if not buggy_path.exists() and not fixed_path.exists():
                    buggy_path.mkdir(parents=True)
                    fixed_path.mkdir(parents=True)
                else:
                    continue

                # check out the branch containing the bug
                cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout %s;" % (self.path, bug_branch)
                subprocess.call(cmd, shell=True)

                # copy all files to the fixed folder
                cmd = "cd %s; cp -r . %s;" % (self.path, fixed_path)
                subprocess.call(cmd, shell=True)

                # check out buggy commit from the branch containing the bug
                cmd = "cd %s; git log --format=format:%%H --grep='Changes in the tests';" % self.path
                buggy_commit = subprocess.check_output(cmd, shell=True).decode("utf-8")
                if len(buggy_commit) == 0:
                    cmd = "cd %s; git log --format=format:%%H --grep='Bug commit';" % self.path
                    buggy_commit = subprocess.check_output(cmd, shell=True).decode("utf-8")

                cmd = "cd %s; git checkout %s;" % (self.path, buggy_commit)
                subprocess.call(cmd, shell=True)

                # copy all files to the bug folder
                cmd = "cd %s; cp -r . %s;" % (self.path, buggy_path)
                subprocess.call(cmd, shell=True)

                # check out master
                cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout andre;" % self.path
                subprocess.call(cmd, shell=True)

                # copy compilation and testing scripts
                cmd = "cd %s; cp compile_bug.py %s; cp compile_bug.py %s; cp run_tests_bug.py %s; cp run_tests_bug.py %s" % (pathlib.Path(self.path, "scripts"), buggy_path, fixed_path, buggy_path, fixed_path)
                subprocess.call(cmd, shell=True)

                # add bug
                self.add_bug(BearsBug(bug_id, fixed_path, utils.get_diff(fixed_path, buggy_path)))

                # remove buggy code
                shutil.rmtree(buggy_path)


    def check_integrity(self, storage: pathlib.Path) -> bool:
        # check out master
        cmd = "cd %s; git reset .; git checkout -- .; git clean -f; git checkout andre;" % self.path
        subprocess.call(cmd, shell=True)

        # get all bugs
        bugs = None
        if pathlib.Path(self.path, "scripts/data/bug_id_and_branch.json").exists():
            with open(pathlib.Path(self.path, "scripts", "data", "bug_id_and_branch.json"), 'r') as f:
                bugs = json.load(f)

        # Checkout all buggy and fixed versions
        missing = set()
        if bugs is not None:
            for bug in bugs:
                bug_id = bug["bugId"]
                bug_branch = bug["bugBranch"]

                fixed_path = pathlib.Path(storage, self.identifier, "%s" % bug_id).absolute()
                if not fixed_path.exists():
                    missing.add(bug_id)

        return len(missing) == 0
