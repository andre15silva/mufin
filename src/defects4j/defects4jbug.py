import pathlib
import subprocess
import re

from bug import Bug

class Defects4JBug(Bug):
    """
    The class for representing Defects4J bugs
    """

    def __init__(self, pid: str, bid: int, path: pathlib.Path, buggy: bool) -> None:
        super().__init__("%s-%d" % (pid, bid), path, buggy)
        self.pid = pid
        self.bid = bid

    def compile(self) -> bool:
        run = subprocess.run("cd %s; defects4j compile" % self.path.absolute(), shell=True, capture_output=True)
        return run.returncode == 0

    def test(self) -> bool:
        run = subprocess.run("cd %s; defects4j test" % self.path.absolute(), shell=True, capture_output=True)
        m = re.search(r"Failing tests: ([0-9]+)", run.stdout.decode("utf-8"))
        return run.returncode == 0 and m != None and int(m.group(1)) == 0

    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
