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
        try:
            run = subprocess.run("cd %s; mvn clean compile" % self.path.absolute(), shell=True, capture_output=True, timeout=60*10)
            return CompileResult(True, run.returncode == 0)
        except subprocess.TimeoutExpired:
            run.terminate()
            return CompileResult(False, False)

    def test_impl(self) -> TestResult:
        try:
            run = subprocess.run("cd %s; mvn clean test" % self.path.absolute(), shell=True, capture_output=True, timeout=60*10)
            return TestResult(True, run.returncode == 0)
        except subprocess.TimeoutExpired:
            run.terminate()
            return TestResult(False, False)
