import pathlib
from abc import ABC, abstractmethod

class Bug(ABC):
    """
    The abstract class for representing a bug.
    """
    
    def __init__(self, identifier: str, path: pathlib.Path, buggy: bool) -> None:
        self.identifier = identifier
        self.path = path
        self.buggy = buggy

    def get_identifier(self) -> str:
        return "%s-%s" % (self.identifier, "buggy" if self.buggy else "fixed")

    def get_path(self) -> pathlib.Path:
        return self.path

    def cwd(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def compile(self) -> bool:
        pass

    @abstractmethod
    def test(self) -> bool:
        pass

    @abstractmethod
    def apply_diff(self, diff: pathlib.Path) -> bool:
        pass

    def __eq__(self, other):
        return self.identifier == other.identifier and self.buggy == other.buggy

    def __hash__(self):
        return hash((self.identifier, self.buggy))

    def __repr__(self):
        return self.get_identifier()
