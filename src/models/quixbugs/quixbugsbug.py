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
        try:
            run = subprocess.run("cd %s/java_programs; javac *.java" % self.path.absolute(), shell=True, capture_output=True, timeout=10)
            return CompileResult(True, run.returncode == 0)
        except:
            run.terminate()
            return CompileResult(False, False)

    def test_impl(self) -> TestResult:
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

                try:
                    cmd = "cd %s; java JavaDeserialization %s %s" % (self.path, self.identifier, " ".join([json.dumps(arg) for arg in copy.deepcopy(test_in)]))
                    java_run = subprocess.run(cmd, shell=True, capture_output=True, universal_newlines=True, timeout=10)

                    cmd = "cd %s; python -c \"from %s import *; print(%s(%s))\"" % (pathlib.Path(self.path, "correct_python_programs"), self.identifier, self.identifier, ",".join([json.dumps(arg) for arg in copy.deepcopy(test_in)]))
                    python_run = subprocess.run(cmd, shell=True, capture_output=True, universal_newlines=True, timeout=10)

                    return TestResult(True, java_run.returncode == 0 and python_run.returncode == 0 and java_run.stdout == python_run.stdout)
                except subprocess.TimeoutExpired:
                    java_run.terminate()
                    python_run.terminate()
                    return TestResult(True, False)
        else:
            return TestResult(False, False)
