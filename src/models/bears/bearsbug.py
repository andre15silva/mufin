import pathlib
import os
import signal
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
        cmd = "cd %s; timeout 600 python2 compile_bug.py --bugId %s --workspace %s" % (self.path, pathlib.Path(self.path).name, pathlib.Path(self.path, ".."))
        run = subprocess.run(cmd, shell=True, capture_output=True)
        return CompileResult(True, run.returncode == 0)

    def test_impl(self) -> TestResult:
        cmd = "cd %s; timeout 600 python2 run_tests_bug.py --bugId %s --workspace %s" % (self.path, pathlib.Path(self.path).name, pathlib.Path(self.path, ".."))
        run = subprocess.run(cmd, shell=True, capture_output=True, timeout=60*10)
        return TestResult(True, run.returncode == 0)
