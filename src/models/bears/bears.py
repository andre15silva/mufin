import pathlib
import subprocess
import json
import shutil

import utils
from models.bug import Bug
from models.dataset import Dataset
from models.bears.bearsbug import BearsBug

class Bears(Dataset):
    
    def __init__(self, path: pathlib.Path) -> None:
        super().__init__("bears", path)

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

                if int(bug_id.split("-")[1]) >= 5:
                    continue

                fixed_path = pathlib.Path(storage, self.identifier, "%s" % bug_id).absolute()
                if not fixed_path.exists():
                    missing.add(bug_id)

        return len(missing) == 0
