import pathlib
import subprocess
import re

from models.bug import Bug

class QuixBugsBug(Bug):
    """
    The class for representing QuixBugs bugs
    """

    def compile(self) -> bool:
        raise NotImplementedError

    def test(self) -> bool:
        raise NotImplementedError

    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
