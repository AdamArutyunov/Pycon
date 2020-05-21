class Verdict:
    def __init__(self, is_fatal, representation, time=0, memory=0):
        self.is_fatal = is_fatal
        self.representation = representation
        self.time = time
        self.memory = memory

    def __str__(self):
        return self.representation


class TestingVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(False, "TG", *args, **kwargs)


class OKVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(False, "OK", *args, **kwargs)


class CompilationErrorVerdict(Verdict):
    def __init__(self):
        super().__init__(True, "CE", time=-1)


class RuntimeErrorVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(True, "RE", *args, **kwargs)


class TimeLimitVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(True, "TL", *args, **kwargs)


class MemoryLimitVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(True, "ML", *args, **kwargs)


class WrongAnswerVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(True, "WA", *args, **kwargs)
