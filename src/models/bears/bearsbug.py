import pathlib
import subprocess
import re

from models.bug import Bug
from models.test_result import TestResult
from models.compile_result import CompileResult

class BearsBug(Bug):
    """
    The class for representing Bears bugs
    """

    def compile_impl(self) -> CompileResult:
        cmd = "cd %s; python2 compile_bug.py --bugId %s --workspace %s" % (self.path, self.get_identifier(), pathlib.Path(self.path, ".."))
        try:
            run = subprocess.run(cmd, shell=True, capture_output=True, timeout=60*10)
            return CompileResult(True, run.returncode == 0)
        except subprocess.TimeoutExpired:
            return CompileResult(False, False)

    def test_impl(self) -> TestResult:
        cmd = "cd %s; python2 run_tests_bug.py --bugId %s --workspace %s" % (self.path, self.get_identifier(), pathlib.Path(self.path, ".."))
        try:
            run = subprocess.run(cmd, shell=True, capture_output=True, timeout=60*10)
            print(run.stdout[-250:])
            return TestResult(True, run.returncode == 0)
        except subprocess.TimeoutExpired:
            return TestResult(False, False)
