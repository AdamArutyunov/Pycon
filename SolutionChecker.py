import sys
import os
import shutil
import subprocess
from time import time
from random import randint
from data import db_session
from data.models.submission import Submission
from sqlalchemy.orm import scoped_session
from flask_login import current_user
from Constants import *
from lib.Verdicts import *


class SolutionChecker:
    def __init__(self):
        self.queue = []
        db_session.global_init(DATABASE_URI)
        db_session.create_session()
        os.chdir(APP_ROOT)

    def submit(self, problem, data):
        session = db_session.create_session()
        user = session.merge(current_user)
        problem = session.merge(problem)
        
        submission = Submission()
        submission.submitter = user
        submission.problem = problem
        submission.data = data

        session.add(submission)
        session.commit()

    def parse(self):
        session = db_session.create_session()
        while True:
            submissions = session.query(Submission).filter(Submission.verdict == None).all()
            for submission in submissions:
                submission.set_verdict(TestingVerdict())
                session.commit()
                self.check_submission(submission)

    def check_submission(self, submission):
        session = db_session.create_session()

        verdict = self.check_solution(submission)
        submission.set_verdict(verdict)

        session.commit()

    def check_solution(self, submission):
        session = db_session.create_session()
        
        test_solution = submission.data
        submitter = submission.submitter
        problem = submission.problem
        solution = submission.data
        tests = problem.tests
        time_limit = problem.time_limit
        memory_limit = problem.memory_limit
        for test in tests:
            submission.set_current_test(test)
            session.commit()
            
            verdict = self.check_test(test, solution, time_limit, memory_limit)
            if verdict.is_fatal:
                submitter.unsolve_problem(problem)
                return verdict

        submitter.solve_problem(problem)
        return OKVerdict()

    def check_test(self, test, solution, time_limit, memory_limit):
        with open('temp/input.txt', 'w+') as f:
            f.write(test.input_data)

        with open('temp/solution.py', 'w+') as f:
            f.write(solution)

        start_time = time()
        try:
            run = subprocess.run([PYTHON_COMMAND, "temp/solution.py"], stdin=open('temp/input.txt', 'r'),
                           stdout=open('temp/output.txt', 'w+'), stderr=open('temp/error.txt', 'w+'),
                           timeout=time_limit)
            end_time = time()
            process_time = int((end_time - start_time) * 1000)
            run.check_returncode()
        except subprocess.CalledProcessError as e:
            end_time = time()
            process_time = int((end_time - start_time) * 1000)
            error = open('temp/error.txt').read().strip().split('\n')[-1].split(':')[0]
            if error == 'SyntaxError':
                return CompilationErrorVerdict()
            return RuntimeErrorVerdict(time=process_time)
        except subprocess.TimeoutExpired:
            end_time = time()
            process_time = int((end_time - start_time) * 1000)
            return TimeLimitVerdict(time=process_time)
        
        with open('temp/output.txt') as f:
            output = f.read().strip()

        if output == test.output_data:
            return OKVerdict(time=process_time)
        return WrongAnswerVerdict(time=process_time)
        
