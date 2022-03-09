import pathlib

from bug import Bug

class Defects4JBug(Bug):
    """
    The class for representing Defects4J bugs
    """

    def __init__(self, pid: str, bid: int, path: pathlib.Path, buggy: bool) -> None:
        super().__init__("%s-%d" % (pid, bid), path, buggy)
        self.pid = pid
        self.bid = bid

    def compile(self) -> int:
        raise NotImplementedError

    def test(self) -> int:
        raise NotImplementedError

    def apply_diff(self, diff: pathlib.Path) -> bool:
        raise NotImplementedError
