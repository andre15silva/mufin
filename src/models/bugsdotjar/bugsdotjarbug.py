import pathlib
import subprocess
import re

from models.bug import Bug
from models.test_result import TestResult

class BugsDotJarBug(Bug):
    """
    The class for representing BugsDorJar bugs
    """

    def compile(self) -> bool:
        try:
            run = subprocess.run("cd %s; mvn clean compile" % self.path.absolute(), shell=True, capture_output=True, timeout=60*10)
            return run.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def test(self) -> TestResult:
        try:
            run = subprocess.run("cd %s; mvn clean test" % self.path.absolute(), shell=True, capture_output=True, timeout=60*10)
            return TestResult(True, run.returncode == 0)
        except subprocess.TimeoutExpired:
            return TestResult(False, False)

    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
