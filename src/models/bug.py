import pathlib
import subprocess
from abc import ABC, abstractmethod
from typing import final

from models.test_result import TestResult
from models.compile_result import CompileResult

class Bug(ABC):
    """
    The abstract class for representing a bug.
    """
    
    def __init__(self, identifier: str, path: pathlib.Path, diff: str) -> None:
        self.identifier = identifier
        self.path = path
        self.diff = diff

    def get_identifier(self) -> str:
        return self.identifier

    def get_path(self) -> pathlib.Path:
        return self.path

    def get_diff(self) -> str:
        return self.diff

    @final
    def checkout(self) -> bool:
        if self.diff == "": return True
        cmd = "cd %s; echo \"%s\" | patch -p0 -d /" % (self.path, self.diff)
        run = subprocess.run(cmd, shell=True, capture_output=True)
        return run.returncode == 0

    @final
    def restore(self) -> bool:
        if self.diff == "": return True
        cmd = "cd %s; echo \"%s\" | patch -p0 -d / -R" % (self.path, self.diff)
        run = subprocess.run(cmd, shell=True, capture_output=True)
        return run.returncode == 0

    @final
    def compile(self) -> CompileResult:
        if not self.checkout():
            return CompileResult(False, False)

        result = CompileResult(False, False)
        try:
            result = self.compile_impl()
        except Exception as e:
            print("Exception: " + str(e))

        if not self.restore():
            return CompileResult(False, False)
        return result

    @final
    def compile_fixed(self) -> CompileResult:
        result = CompileResult(False, False)
        try:
            result = self.compile_impl()
        except Exception as e:
            print("Exception: " + str(e))
            return CompileResult(False, False)
        return result

    @abstractmethod
    def compile_impl(self) -> CompileResult:
        pass

    @final
    def test(self) -> TestResult:
        if not self.checkout():
            return TestResult(False, False)

        result = TestResult(False, False)
        try:
            result = self.test_impl()
        except Exception as e:
            print("Exception: " + str(e))

        if not self.restore():
            return TestResult(False, False)
        return result

    @final
    def test_fixed(self) -> TestResult:
        result = TestResult(False, False)
        try:
            result = self.test_impl()
        except Exception as e:
            print("Exception: " + str(e))
            return TestResult(False, False)
        return result

    @abstractmethod
    def test_impl(self) -> TestResult:
        pass

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)

    def __repr__(self):
        return self.get_identifier()
