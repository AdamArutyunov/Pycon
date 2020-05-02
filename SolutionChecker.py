import sys
from time import sleep
from subprocess import Popen
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
        solution = problem.solution
        tests = problem.tests
        
        sleep(5)  # Temp
        
        for test in problem.tests:
            submission.set_current_test(test)
            session.commit()
            
            verdict = self.check_test(test, test_solution, solution)
            if verdict.is_fatal and False:
                if (problem not in submitter.solved_problems and
                        problem not in submitter.unsolved_problems):
                    submitter.unsolved_problems.append(problem)                    
                return verdict

        if problem not in submitter.solved_problems:
            if problem in submitter.unsolved_problems:
                print(submitter.unsolved_problems)
                submitter.unsolved_problems.remove(problem)
            submitter.solved_problems.append(problem)

        return OKVerdict()

    def check_test(self, test, test_solution, solution):
        sleep(5)  # Temp
        verdicts = [OKVerdict, CompilationErrorVerdict, RuntimeErrorVerdict,
                    TimeLimitVerdict, MemoryLimitVerdict, WrongAnswerVerdict]
        from random import choice, randint

        verdict = choice(verdicts)()
        verdict.time = randint(100, 2000)
        verdict.memory = randint(0, 10240)

        return verdict
        
        
        
