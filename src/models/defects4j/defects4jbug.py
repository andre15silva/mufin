import pathlib
import subprocess
import re

from models.bug import Bug
from models.test_result import TestResult
from models.compile_result import CompileResult

class Defects4JBug(Bug):
    """
    The class for representing Defects4J bugs
    """

    def compile_impl(self) -> CompileResult:
        try:
            run = subprocess.run("cd %s; defects4j compile" % self.path.absolute(), shell=True, capture_output=True, timeout=60*10)
            return CompileResult(True, run.returncode == 0)
        except subprocess.TimeoutExpired:
            run.terminate()
            return CompileResult(False, False)

    def test_impl(self) -> TestResult:
        try:
            run = subprocess.run("cd %s; defects4j test" % self.path.absolute(), shell=True, capture_output=True, timeout=60*10)
            m = re.search(r"Failing tests: ([0-9]+)", run.stdout.decode("utf-8"))
            return TestResult(True and m != None, run.returncode == 0 and int(m.group(1)) == 0)
        except subprocess.TimeoutExpired:
            run.terminate()
            return TestResult(False, False)
