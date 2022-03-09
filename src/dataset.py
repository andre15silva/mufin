import pathlib
from abc import ABC, abstractmethod

from bug import Bug
from typing import Set

class Dataset(ABC):
    """
    The abstract class for representing a dataset.
    """

    def __init__(self, identifier: str, path: pathlib.Path) -> None:
        self.identifier = identifier
        self.path = path
        self.bugs = set()

    def get_identifier(self) -> int:
        return self.identifier

    def get_path(self) -> pathlib.Path:
        return self.path

    def get_bugs(self) -> Set[Bug]:
        return self.bugs

    def cwd(self) -> None:
        Path.cwd()

    @abstractmethod
    def add_bug(self, bug: Bug) -> None:
        pass

    @abstractmethod
    def checkout_all(self, storage: pathlib.Path) -> None:
        pass

    @abstractmethod
    def check_integrity(self) -> bool:
        pass
