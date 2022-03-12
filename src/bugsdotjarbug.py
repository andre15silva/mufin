import pathlib
import subprocess
import re

from bug import Bug

class BugsDotJarBug(Bug):
    """
    The class for representing BugsDorJar bugs
    """

    def compile(self) -> bool:
        run = subprocess.run("cd %s; mvn compile" % self.path.absolute(), shell=True, capture_output=True)
        return run.returncode == 0

    def test(self) -> bool:
        run = subprocess.run("cd %s; mvn test" % self.path.absolute(), shell=True, capture_output=True)
        return run.returncode == 0

    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
