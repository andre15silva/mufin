import pathlib
import subprocess
import re

from models.bug import Bug
from models.test_result import TestResult
from models.compile_result import CompileResult

class BugsDotJarBug(Bug):
    """
    The class for representing BugsDorJar bugs
    """

    def compile_impl(self) -> CompileResult:
        run = subprocess.run("cd %s; timeout 30 mvn clean compile" % self.path.absolute(), shell=True, capture_output=True)
        return CompileResult(True, run.returncode == 0)

    def test_impl(self) -> TestResult:
        run = subprocess.run("cd %s; timeout 120 mvn clean test" % self.path.absolute(), shell=True, capture_output=True)
        return TestResult(True, run.returncode == 0)
