class Verdict:
    def __init__(self, is_fatal, representation):
        self.is_fatal = is_fatal
        self.representation = representation
        self.time = 0
        self.memory = 0

    def __str__(self):
        return self.representation


class TestingVerdict(Verdict):
    def __init__(self):
        super().__init__(False, "TG")


class OKVerdict(Verdict):
    def __init__(self):
        super().__init__(False, "OK")


class CompilationErrorVerdict(Verdict):
    def __init__(self):
        super().__init__(True, "CE")


class RuntimeErrorVerdict(Verdict):
    def __init__(self):
        super().__init__(True, "RE")


class TimeLimitVerdict(Verdict):
    def __init__(self):
        super().__init__(True, "TL")


class MemoryLimitVerdict(Verdict):
    def __init__(self):
        super().__init__(True, "ML")


class WrongAnswerVerdict(Verdict):
    def __init__(self):
        super().__init__(True, "WA")
