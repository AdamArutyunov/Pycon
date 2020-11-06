import os
import subprocess
import psutil
from time import time
from data import db_session
from data.models.submission import Submission
from flask_login import current_user
from Constants import *
from lib.Verdicts import *
from lib.Languages import *


class SolutionChecker:
    def __init__(self):
        self.queue = []
        db_session.global_init(DATABASE_URI)
        db_session.create_session()
        os.chdir(APP_ROOT)

    def submit(self, problem, language, data):
        session = db_session.create_session()
        user = session.merge(current_user)
        problem = session.merge(problem)

        submission = Submission()
        submission.submitter = user
        submission.problem = problem
        submission.language = language
        submission.data = data

        session.add(submission)
        session.commit()

    def parse(self):
        session = db_session.create_session()
        while True:
            submissions = session.query(Submission).filter(Submission.verdict == 0).all()
            for submission in submissions:
                submission.set_verdict(TestingVerdict())
                session.commit()

                try:
                    self.check_submission(submission)
                except Exception as e:
                    print(e)
                    submission.set_verdict(TestingErrorVerdict())

                session.commit()

    def check_submission(self, submission):
        session = db_session.create_session()

        verdict = self.check_solution(submission)
        submission.set_verdict(verdict)

        session.commit()

    def check_solution(self, submission):
        session = db_session.create_session()

        submitter = submission.submitter
        problem = submission.problem
        solution = submission.data
        submission_language = submission.language
        tests = problem.tests
        time_limit = problem.time_limit
        memory_limit = problem.memory_limit

        language = LANGUAGES[submission_language]
        if language.id == 1:
            TestChecker = PythonTestChecker
        elif language.id == 2:
            TestChecker = CSharpTestChecker

        compilation_verdict = TestChecker.compile(solution, time_limit, memory_limit)
        if compilation_verdict:
            submitter.unsolve_problem(problem)
            return compilation_verdict

        for i, test in enumerate(tests):
            submission.set_current_test(i + 1)
            session.commit()

            verdict = TestChecker.check_test(test, solution, time_limit, memory_limit)
            if verdict.is_fatal:
                submitter.unsolve_problem(problem)
                return verdict

        submitter.solve_problem(problem)
        return OKVerdict()


class PythonTestChecker:
    @staticmethod
    def compile(solution, time_limit, memory_limit):
        with open('temp/solution.py', 'w+') as f:
            f.write(solution)

    @staticmethod
    def check_test(test, solution, time_limit, memory_limit):
        MAX_MEMORY = memory_limit * 1024 * 1024
        verdict = None

        with open('temp/input.txt', 'w+') as f:
            f.write(test.input_data)

        start_time = time()
        try:
            run = subprocess.Popen([PYTHON_COMMAND, "temp/solution.py"], stdin=open('temp/input.txt', 'r'),
                                   stdout=open('temp/output.txt', 'w+'), stderr=open('temp/error.txt', 'w+'))
            proc = psutil.Process(run.pid)

            if os.name == "posix":
                proc.rlimit(psutil.RLIMIT_AS, (MAX_MEMORY, MAX_MEMORY))

            returncode = proc.wait(timeout=time_limit)

            if returncode:
                raise subprocess.CalledProcessError(returncode, PYTHON_COMMAND)
        except subprocess.CalledProcessError as e:
            error = open('temp/error.txt').read().strip().split('\n')[-1].split(':')[0]
            if error == 'SyntaxError':
                return CompilationErrorVerdict()
            if error == 'MemoryError':
                verdict = MemoryLimitVerdict
            else:
                verdict = RuntimeErrorVerdict
        except psutil.TimeoutExpired:
            proc.kill()
            verdict = TimeLimitVerdict
        finally:
            end_time = time()
            process_time = int((end_time - start_time) * 1000)

            if verdict:
                return verdict(time=process_time)

        with open('temp/output.txt') as f:
            output = f.read().strip()

        if output == test.output_data:
            verdict = OKVerdict
        else:
            verdict = WrongAnswerVerdict

        return verdict(time=process_time)


class CSharpTestChecker:
    @staticmethod
    def compile(solution, time_limit, memory_limit):
        MAX_MEMORY = memory_limit * 1024 * 1024
        verdict = None

        with open('temp/solution.cs', 'w+') as f:
            f.write(solution)

        start_time = time()
        try:
            run = subprocess.Popen([CSHARP_COMPILE_COMMAND, "temp/solution.cs"], stdin=open('temp/input.txt', 'r'),
                                   stdout=open('temp/output.txt', 'w+'), stderr=open('temp/error.txt', 'w+'))
            proc = psutil.Process(run.pid)

            if os.name == "posix":
                proc.rlimit(psutil.RLIMIT_AS, (MAX_MEMORY, MAX_MEMORY))

            returncode = proc.wait(timeout=time_limit)

            if returncode:
                raise subprocess.CalledProcessError(returncode, CSHARP_COMPILE_COMMAND)
        except subprocess.CalledProcessError as e:
            verdict = CompilationErrorVerdict
        except psutil.TimeoutExpired:
            proc.kill()
            verdict = CompilationErrorVerdict
        finally:
            if verdict:
                return verdict()

    @staticmethod
    def check_test(test, solution, time_limit, memory_limit):
        MAX_MEMORY = memory_limit * 1024 * 1024
        verdict = None

        with open('temp/input.txt', 'w+') as f:
            f.write(test.input_data)

        start_time = time()
        try:
            run = subprocess.Popen([CSHARP_RUN_COMMAND, "temp/solution.exe"], stdin=open('temp/input.txt', 'r'),
                                   stdout=open('temp/output.txt', 'w+'), stderr=open('temp/error.txt', 'w+'))

            proc = psutil.Process(run.pid)

            if os.name == "posix":
                proc.rlimit(psutil.RLIMIT_AS, (MAX_MEMORY, MAX_MEMORY))

            proc.wait(timeout=time_limit)

            run.communicate()

            if run.returncode:
                raise subprocess.CalledProcessError(-1, CSHARP_RUN_COMMAND)
        except subprocess.CalledProcessError as e:
            verdict = RuntimeErrorVerdict
        except psutil.TimeoutExpired:
            proc.kill()
            verdict = TimeLimitVerdict
        finally:
            end_time = time()
            process_time = int((end_time - start_time) * 1000)

            if verdict:
                return verdict(process_time)

        with open('temp/output.txt') as f:
            output = f.read().strip()

        if output == test.output_data:
            verdict = OKVerdict
        else:
            verdict = WrongAnswerVerdict

        return verdict(time=process_time)
