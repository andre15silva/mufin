import pathlib
import subprocess
import re

from models.bug import Bug
from models.test_result import TestResult

class BearsBug(Bug):
    """
    The class for representing Bears bugs
    """

    def compile(self) -> bool:
        cmd = "cd %s; python2 compile_bug.py --bugId %s --workspace %s" % (self.path, self.get_identifier(), pathlib.Path(self.path, ".."))
        try:
            run = subprocess.run(cmd, shell=True, capture_output=True, timeout=60*10)
            return run.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def test(self) -> TestResult:
        cmd = "cd %s; python2 run_tests_bug.py --bugId %s --workspace %s" % (self.path, self.get_identifier(), pathlib.Path(self.path, ".."))
        try:
            run = subprocess.run(cmd, shell=True, capture_output=True, timeout=60*10)
            return TestResult(True, run.returncode == 0)
        except subprocess.TimeoutExpired:
            return TestResult(False, False)

    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
