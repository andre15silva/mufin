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
        # TODO: We need access to the bears repo
        raise NotImplementedError

    def test(self) -> TestResult:
        # TODO: We need access to the bears repo
        raise NotImplementedError

    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
