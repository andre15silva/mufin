import pathlib
import subprocess
import os
import shutil

import utils
from models.bug import Bug
from models.dataset import Dataset
from models.bugsdotjar.bugsdotjarbug import BugsDotJarBug

class BugsDotJar(Dataset):

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__("bugsdotjar", path)

    
    def checkout_oldests(self, storage: pathlib.Path) -> None:
        raise NotImplementedError

    def check_oldests(self, storage: pathlib.Path) -> bool:
        raise NotImplementedError


    def checkout_all(self, storage: pathlib.Path) -> None:
        bugs = None
        directories = [x for x in self.path.iterdir() if pathlib.Path(self.path, x).is_dir()]

        for project in directories:
            # get all bug branches
            project_path = pathlib.Path(self.path, project).absolute()
            cmd = "cd %s; git branch -a | grep \"bugs-dot-jar_\" ;" % project_path.absolute()
            bug_branches = [x.decode("utf-8") for x in subprocess.check_output(cmd, shell = True).split()]

            for branch in bug_branches:
                # checkout buggy branch and copy to the bug folder
                bug = branch
                if "/" in branch: bug = branch.split("/")[-1]
                if not bug.startswith("bugs-dot-jar_"): continue

                # compute paths
                buggy_path = pathlib.Path(storage, self.identifier, "%s-buggy" % bug).absolute()
                fixed_path = pathlib.Path(storage, self.identifier, "%s" % bug).absolute()
                if not buggy_path.exists() and not fixed_path.exists():
                    buggy_path.mkdir(parents=True)
                    fixed_path.mkdir(parents=True)

                # copy to buggy path
                cmd = "cd %s; git checkout %s; cp -r . %s;" % (project_path, bug, buggy_path)
                subprocess.call(cmd, shell=True)

                # copy to fixed path
                cmd = "cd %s; git checkout %s; cp -r . %s;" % (project_path, bug, fixed_path)
                subprocess.call(cmd, shell=True)

                # apply patch in fixed version
                cmd = "cd %s; patch -p1 < .bugs-dot-jar/developer-patch.diff;" % fixed_path
                subprocess.call(cmd, shell=True)

                # add bug
                self.add_bug(BugsDotJarBug(bug, fixed_path, utils.get_diff(fixed_path, buggy_path)))

                # remove buggy code
                shutil.rmtree(buggy_path)


    def check_integrity(self, storage: pathlib.Path) -> bool:
        directories = [x for x in self.path.iterdir() if pathlib.Path(self.path, x).is_dir()]

        missing = set()
        for project in directories:
            # get all bug branches
            project_path = pathlib.Path(self.path, project).absolute()
            cmd = "cd %s; git branch -a | grep \"bugs-dot-jar_\" ;" % project_path.absolute()
            bug_branches = [x.decode("utf-8") for x in subprocess.check_output(cmd, shell = True).split()]

            for branch in bug_branches:
                bug = branch
                if "/" in branch: bug = branch.split("/")[-1]
                if not bug.startswith("bugs-dot-jar_"): continue

                # copy to buggy path
                fixed_path = pathlib.Path(storage, self.identifier, "%s" % bug).absolute()
                if not fixed_path.exists():
                    missing.add(bug)

        return len(missing) == 0
