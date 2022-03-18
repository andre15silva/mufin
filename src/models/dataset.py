import pathlib
from abc import ABC, abstractmethod

from models.bug import Bug
from typing import Set

class Dataset(ABC):
    """
    The abstract class for representing a dataset.
    """

    def __init__(self, identifier: str, path: pathlib.Path) -> None:
        self.identifier = identifier
        self.path = path.absolute()
        self.bugs = set()

    def get_identifier(self) -> str:
        return self.identifier

    def get_path(self) -> pathlib.Path:
        return self.path

    def get_bugs(self) -> Set[Bug]:
        return self.bugs

    def cwd(self) -> None:
        Path.cwd()

    def add_bug(self, bug: Bug) -> None:
        self.bugs.add(bug)

    @abstractmethod
    def checkout_all(self, storage: pathlib.Path) -> None:
        pass

    @abstractmethod
    def check_integrity(self, storage: pathlib.Path) -> bool:
        pass
