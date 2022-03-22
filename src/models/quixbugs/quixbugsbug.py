import pathlib
import subprocess
import re
import json
import copy

from models.bug import Bug

class QuixBugsBug(Bug):
    """
    The class for representing QuixBugs bugs
    """

    def compile(self) -> bool:
        run = subprocess.run("cd %s/java_programs; javac *.java" % self.path.absolute(), shell=True, capture_output=True)
        return run.returncode == 0

    def test(self) -> bool:
        # Not a graph based bug, so we need to run both the python and Java versions
        if pathlib.Path(self.path, "JavaDeserialization.java").exists():
            # Code adapted from QuixBugs tester.py script
            with open(pathlib.Path(self.path, "json_testcases", self.identifier + ".json"), 'r') as working_file:
                for line in working_file:
                    py_testcase = json.loads(line)
                test_in, test_out = py_testcase
                if not isinstance(test_in, list):
                    # input is required to be a list, as multiparameter algos need to deconstruct a list of parameters
                    # should fix in testcases, force all inputs to be list of inputs
                    test_in = [test_in]
                    # unsure how to make immutable; previous versions just used copy.deepcopy

                cmd = "cd %s; java JavaDeserialization %s %s" % (self.path, self.identifier, " ".join([json.dumps(arg) for arg in copy.deepcopy(test_in)]))
                try:
                    run = subprocess.run(cmd, shell=True, capture_output=True, universal_newlines=True, timeout=10)
                    # TODO: Compare output with right version
                    return run.returncode == 0
                except subprocess.TimeoutExpired:
                    return False
        else:
            return True


    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
