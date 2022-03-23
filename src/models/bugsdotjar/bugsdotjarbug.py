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
        run = subprocess.run("cd %s; mvn clean compile" % self.path.absolute(), shell=True, capture_output=True)
        return run.returncode == 0

    def test(self) -> TestResult:
        run = subprocess.run("cd %s; mvn clean test" % self.path.absolute(), shell=True, capture_output=True)
        return TestResult(True, run.returncode == 0)

    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
