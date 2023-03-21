import pathlib
import subprocess
import shutil

import utils
from models.bug import Bug
from models.dataset import Dataset
from models.quixbugs.quixbugsbug import QuixBugsBug

class QuixBugs(Dataset):

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__("quixbugs", path)


    def checkout_oldests(self, storage: pathlib.Path) -> None:
        raise NotImplementedError

    def check_oldests(self, storage: pathlib.Path) -> bool:
        raise NotImplementedError


    def checkout_all(self, storage: pathlib.Path) -> None:
        algos = [x.stem for x in pathlib.Path(self.path, "java_programs").iterdir() if ".java" in str(x) and x.stem.isupper()]

        for algo in algos:
            buggy_path = pathlib.Path(storage, self.identifier, "%s-buggy" % algo.lower()).absolute()
            fixed_path = pathlib.Path(storage, self.identifier, "%s" % algo.lower()).absolute()
            if buggy_path.exists() or fixed_path.exists(): continue
            buggy_path.mkdir(parents=True)
            fixed_path.mkdir(parents=True)

            # Copy files to buggy path
            # Copy source files
            cmd = "cd %s; mkdir %s/java_programs; cp java_programs/%s.java %s/java_programs/; cp java_programs/Node.java %s/java_programs/; cp java_programs/WeightedEdge.java %s/java_programs/" % (self.path, buggy_path, algo, buggy_path, buggy_path, buggy_path)
            subprocess.call(cmd, shell=True)
            # Copy test files
            cmd = "cd %s; mkdir -p %s/java_testcases/junit; cp java_testcases/junit/%s_TEST.java %s/java_testcases/junit" % (self.path, buggy_path, algo, buggy_path)
            subprocess.call(cmd, shell=True)
            # Copy build.gradle
            cmd = "cd %s; cp build.gradle %s/" % (self.path, buggy_path)
            subprocess.call(cmd, shell=True)

            # Copy files to fixed path
            # Copy source files
            cmd = "cd %s; mkdir %s/java_programs; sed -i \"1s/.*/package java_programs;/\" correct_java_programs/%s.java; cp correct_java_programs/%s.java %s/java_programs/; cp java_programs/Node.java %s/java_programs/; cp java_programs/WeightedEdge.java %s/java_programs/" % (self.path, fixed_path, algo, algo, fixed_path, fixed_path, fixed_path)
            subprocess.call(cmd, shell=True)
            # Copy test files
            cmd = "cd %s; mkdir -p %s/java_testcases/junit; cp java_testcases/junit/%s_TEST.java %s/java_testcases/junit" % (self.path, fixed_path, algo, fixed_path)
            subprocess.call(cmd, shell=True)
            # Copy build.gradle
            cmd = "cd %s; cp build.gradle %s/" % (self.path, fixed_path)
            subprocess.call(cmd, shell=True)

            self.add_bug(QuixBugsBug(algo.lower(), fixed_path, utils.get_diff(fixed_path, buggy_path)))

            # Remove buggy codebase
            shutil.rmtree(buggy_path)

    def check_integrity(self, storage: pathlib.Path) -> bool:
        algos = [x.stem for x in pathlib.Path(self.path, "java_programs").iterdir() if ".java" in str(x) and x.stem.isupper()]

        missing = set()
        for algo in algos:
            fixed_path = pathlib.Path(storage, self.identifier, "%s" % algo.lower()).absolute()
            if not fixed_path.exists():
                missing.add(algo.lower())

        return len(missing) == 0
