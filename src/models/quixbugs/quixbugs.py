import pathlib
import subprocess

import utils
from models.bug import Bug
from models.dataset import Dataset
from models.quixbugs.quixbugsbug import QuixBugsBug

class QuixBugs(Dataset):

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__("quixbugs", path)


    def checkout_all(self, storage: pathlib.Path) -> None:
        algos = [x.stem for x in pathlib.Path(self.path, "java_programs").iterdir() if ".java" in str(x) and x.stem.isupper()]

        for algo in algos:
            buggy_path = pathlib.Path(storage, self.identifier, "%s-buggy" % algo.lower()).absolute()
            fixed_path = pathlib.Path(storage, self.identifier, "%s-fixed" % algo.lower()).absolute()
            if buggy_path.exists() or fixed_path.exists(): continue
            buggy_path.mkdir(parents=True)
            fixed_path.mkdir(parents=True)

            # Copy files to buggy path
            # Copy java files
            cmd = "cd %s; mkdir %s/java_programs; cp java_programs/%s.java %s/java_programs/; cp java_programs/Node.java %s/java_programs/; cp java_programs/WeightedEdge.java %s/java_programs/" % (self.path, buggy_path, algo, buggy_path, buggy_path, buggy_path)
            subprocess.call(cmd, shell=True)
            if pathlib.Path(self.path, "java_testcases", algo + ".java").exists():
                cmd = "cd %s, mkdir %s/java_testcases; cp java_testcases/%s.java %s/java_testcases/" % (self.path, buggy_path, algo, buggy_path)
                subprocess.call(cmd, shell=True)
            # Copy json and JavaDeserialization
            if pathlib.Path(self.path, "json_testcases", algo.lower() + ".json").exists():
                cmd = "cd %s; mkdir %s/json_testcases; cp -r json_testcases/%s.json %s/json_testcases/" % (self.path, buggy_path, algo.lower(), buggy_path)
                subprocess.call(cmd, shell=True)
                cmd = "cd %s; cp JavaDeserialization.* %s/" % (self.path, buggy_path)
                subprocess.call(cmd, shell=True)

            # Copy gson dependency
            cmd = "cd %s; mkdir %s/com; cp -r com/ %s/" % (self.path, buggy_path, buggy_path)
            subprocess.call(cmd, shell=True)
            # Copy python programs
            cmd = "cd %s; mkdir %s/correct_python_programs; cp -r correct_python_programs/%s.py %s/correct_python_programs/" % (self.path, buggy_path, algo.lower(), buggy_path)
            subprocess.call(cmd, shell=True)

            # Copy files to fixed path
            # Copy java files
            cmd = "cd %s; mkdir %s/java_programs; sed -i \"1s/.*/package java_programs;/\" correct_java_programs/%s.java; cp correct_java_programs/%s.java %s/java_programs/; cp java_programs/Node.java %s/java_programs/; cp java_programs/WeightedEdge.java %s/java_programs/" % (self.path, fixed_path, algo, algo, fixed_path, fixed_path, fixed_path)
            subprocess.call(cmd, shell=True)
            if pathlib.Path(self.path, "java_testcases", algo + ".java").exists():
                cmd = "cd %s, mkdir %s/java_testcases; cp java_testcases/%s.java %s/java_testcases/" % (self.path, fixed_path, algo, fixed_path)
                subprocess.call(cmd, shell=True)
            # Copy json and JavaDeserialization
            if pathlib.Path(self.path, "json_testcases", algo.lower() + ".json").exists():
                cmd = "cd %s; mkdir %s/json_testcases; cp -r json_testcases/%s.json %s/json_testcases/" % (self.path, fixed_path, algo.lower(), fixed_path)
                subprocess.call(cmd, shell=True)
                cmd = "cd %s; cp JavaDeserialization.* %s/" % (self.path, fixed_path)
                subprocess.call(cmd, shell=True)
            # Copy gson dependency
            cmd = "cd %s; mkdir %s/com; cp -r com/ %s/" % (self.path, fixed_path, fixed_path)
            subprocess.call(cmd, shell=True)
            # Copy python programs
            cmd = "cd %s; mkdir %s/correct_python_programs; cp -r correct_python_programs/%s.py %s/correct_python_programs/" % (self.path, fixed_path, algo.lower(), fixed_path)
            subprocess.call(cmd, shell=True)

            self.add_bug(QuixBugsBug(algo.lower(), buggy_path, True, utils.get_diff(buggy_path, fixed_path)))
            self.add_bug(QuixBugsBug(algo.lower(), fixed_path, False, utils.get_diff(fixed_path, buggy_path)))

    def check_integrity(self, storage: pathlib.Path) -> bool:
        algos = [x.stem for x in pathlib.Path(self.path, "java_programs").iterdir() if ".java" in str(x) and x.stem.isupper()]

        missing = set()
        for algo in algos:
            buggy_path = pathlib.Path(storage, self.identifier, "%s-buggy" % algo.lower()).absolute()
            fixed_path = pathlib.Path(storage, self.identifier, "%s-fixed" % algo.lower()).absolute()
            if not buggy_path.exists() or not fixed_path.exists():
                missing.add(algo.lower())

        return len(missing) == 0
