import pathlib
import subprocess
import re

from models.bug import Bug
from models.test_result import TestResult

class Defects4JBug(Bug):
    """
    The class for representing Defects4J bugs
    """

    def compile(self) -> bool:
        try:
            run = subprocess.run("cd %s; defects4j compile" % self.path.absolute(), shell=True, capture_output=True, timeout=60*10)
            return run.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def test(self) -> TestResult:
        try:
            run = subprocess.run("cd %s; defects4j test" % self.path.absolute(), shell=True, capture_output=True, timeout=60*10)
            m = re.search(r"Failing tests: ([0-9]+)", run.stdout.decode("utf-8"))
            return TestResult(True, run.returncode == 0 and m != None and int(m.group(1)) == 0)
        except subprocess.TimeoutExpired:
            return TestResult(False, False)

    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
