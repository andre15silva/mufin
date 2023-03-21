import pathlib
import subprocess
import re
import json
import copy

from models.bug import Bug
from models.test_result import TestResult
from models.compile_result import CompileResult

class QuixBugsBug(Bug):
    """
    The class for representing QuixBugs bugs
    """

    def compile_impl(self) -> CompileResult:
        run = subprocess.run("cd %s/java_programs; timeout 600 javac *.java" % self.path.absolute(), shell=True, capture_output=True)
        return CompileResult(True, run.returncode == 0)

    def test_impl(self) -> TestResult:
        # Not a graph based bug, so we need to run both the python and Java versions
        if pathlib.Path(self.path, "JavaDeserialization.java").exists():
            # Code adapted from QuixBugs tester.py script
            with open(pathlib.Path(self.path, "json_testcases", self.identifier.split("-")[0] + ".json"), 'r') as working_file:
                for line in working_file:
                    py_testcase = json.loads(line)
                test_in, test_out = py_testcase
                if not isinstance(test_in, list):
                    # input is required to be a list, as multiparameter algos need to deconstruct a list of parameters
                    # should fix in testcases, force all inputs to be list of inputs
                    test_in = [test_in]
                    # unsure how to make immutable; previous versions just used copy.deepcopy

                cmd = "cd %s; timeout 600 java JavaDeserialization %s %s" % (self.path, self.identifier, " ".join([json.dumps(arg) for arg in copy.deepcopy(test_in)]))
                java_run = subprocess.run(cmd, shell=True, capture_output=True, universal_newlines=True)

                cmd = "cd %s; timeout 600 python -c \"from %s import *; print(%s(%s))\"" % (pathlib.Path(self.path, "correct_python_programs"), self.identifier, self.identifier, ",".join([json.dumps(arg) for arg in copy.deepcopy(test_in)]))
                python_run = subprocess.run(cmd, shell=True, capture_output=True, universal_newlines=True)

                return TestResult(True, java_run.returncode == 0 and python_run.returncode == 0 and java_run.stdout == python_run.stdout)
        else:
            return TestResult(False, False)
