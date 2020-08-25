import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..db_session import SqlAlchemyBase


class UserToContest(SqlAlchemyBase):
    __tablename__ = 'user_to_contest'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    user = orm.relation('User', backref=orm.backref('contests', lazy='joined', cascade='all'))
    contest_id = Column(Integer, ForeignKey('contests.id'), primary_key=True)
    contest = orm.relation('Contest', backref=orm.backref('participants', lazy='joined', cascade='all'))


class UserToProblem(SqlAlchemyBase):
    __tablename__ = 'user_to_problem'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    user = orm.relation('User', backref=orm.backref('problems', lazy='joined', cascade='all'))
    problem_id = Column(Integer, ForeignKey('problems.id'), primary_key=True)
    problem = orm.relation('Problem', backref=orm.backref('users', lazy='joined', cascade='all'))
    solved = Column(Boolean, nullable=False)
    submissions = Column(Integer, default=1)


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = orm.relation('Group')
    role = Column(Integer, default=0)
    submissions = orm.relation("Submission", back_populates='submitter')
    registration_date = Column(DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def is_admin(self):
        if self.role == 1 or self.login == "Adam":
            return True
        return False

    @property
    def solved_problems(self):
        return list(map(lambda x: x.problem, filter(lambda x: x.solved, self.problems)))

    @property
    def unsolved_problems(self):
        return list(map(lambda x: x.problem, filter(lambda x: not x.solved, self.problems)))

    def solve_problem(self, problem):
        problem_association = self.get_problem_association(problem)
        if not problem_association:
            problem_association = UserToProblem()
            problem_association.problem = problem
            problem_association.solved = True
            self.problems.append(problem_association)
        else:
            if problem_association.solved:
                return
            problem_association.submissions += 1
            problem_association.solved = True

    def unsolve_problem(self, problem):
        problem_association = self.get_problem_association(problem)
        if not problem_association:
            problem_association = UserToProblem()
            problem_association.problem = problem
            problem_association.solved = False
            self.problems.append(problem_association)
        else:
            problem_association.submissions += 1

    def get_problem_association(self, problem):
        problem_associations = list(filter(lambda x: x.problem == problem, self.problems))

        if not problem_associations:
            return

        return problem_associations[0]

    def get_contest_association(self, contest):
        contest_associations = list(filter(lambda x: x.contest == contest, self.contests))

        if not contest_associations:
            return

        return contest_associations[0]

    def get_solved_contest_problems_count(self, contest):
        solved_problems_count = 0
        
        for problem in contest.problems:
            problem_association = self.get_problem_association(problem)
            if problem_association and problem_association.solved:
                solved_problems_count += 1

        return solved_problems_count

    def join_contest(self, contest):
        contests = list(map(lambda x: x.contest, self.contests))
        if contest in contests or contest.is_finished():
            return
        
        contest_association = UserToContest()
        contest_association.contest = contest
        self.contests.append(contest_association)
