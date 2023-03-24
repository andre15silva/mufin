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
        run = subprocess.run("cd %s; timeout 600 mvn compile" % self.path.absolute(), shell=True, capture_output=True)
        return CompileResult(True, run.returncode == 0)

    def test_impl(self) -> TestResult:
        run = subprocess.run("cd %s; timeout 600 mvn test" % self.path.absolute(), shell=True, capture_output=True)
        return CompileResult(True, run.returncode == 0)
