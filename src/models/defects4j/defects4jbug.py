import pathlib
import os
import signal
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
        run = subprocess.run("cd %s; timeout 30 defects4j compile" % self.path.absolute(), shell=True, capture_output=True)
        return CompileResult(True, run.returncode == 0)

    def test_impl(self) -> TestResult:
        run = subprocess.run("cd %s; timeout 120 defects4j test" % self.path.absolute(), shell=True, capture_output=True)
        m = re.search(r"Failing tests: ([0-9]+)", run.stdout.decode("utf-8"))
        return TestResult(True and m != None, run.returncode == 0 and int(m.group(1)) == 0)
