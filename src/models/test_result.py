class TestResult:

    def __init__(self, executes: bool, result: bool) -> None:
        self.executes = executes
        self.result = result

    def is_executing(self) -> bool:
        return self.executes

    def is_passing(self) -> bool:
        return self.result
