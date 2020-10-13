class Verdict:
    def __init__(self, verdict_id, is_fatal, representation, display_name="", time=0, memory=0):
        self.id = verdict_id
        self.is_fatal = is_fatal
        self.representation = representation
        self.display_name = display_name
        self.time = time
        self.memory = memory

    def __str__(self):
        return self.representation


class TestingVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(1, False, "TG", "Тестируется", *args, **kwargs)


class OKVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(2, False, "OK", "Полное решение", *args, **kwargs)


class CompilationErrorVerdict(Verdict):
    def __init__(self):
        super().__init__(3, True, "CE", "Ошибка компиляции", time=-1)


class RuntimeErrorVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(4, True, "RE", "Ошибка во время исполнения", *args, **kwargs)


class WrongAnswerVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(5, True, "WA", "Неправильный ответ", *args, **kwargs)


class TimeLimitVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(6, True, "TL", "Превышение лимита времени", *args, **kwargs)


class MemoryLimitVerdict(Verdict):
    def __init__(self, *args, **kwargs):
        super().__init__(7, True, "ML", "Превышение лимита памяти", *args, **kwargs)


VERDICTS = [Verdict, TestingVerdict, OKVerdict, CompilationErrorVerdict, RuntimeErrorVerdict,
            WrongAnswerVerdict, TimeLimitVerdict, MemoryLimitVerdict]
