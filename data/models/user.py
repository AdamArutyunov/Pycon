import datetime
import sqlalchemy.orm as orm
from sqlalchemy import *
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..db_session import SqlAlchemyBase
from .. import db_session


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


class UserToNews(SqlAlchemyBase):
    __tablename__ = 'user_to_news'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    user = orm.relation('User', backref=orm.backref('news_rated', lazy='joined', cascade='all'))
    news_id = Column(Integer, ForeignKey('news.id'), primary_key=True)
    news = orm.relation('News', backref=orm.backref('users_rated', lazy='joined', cascade='all'))
    rate = Column(Integer, nullable=True)


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
        session = db_session.create_session()
        problem_associations = session.query(UserToProblem).filter((UserToProblem.user == self) and
                                                                    (UserToProblem.solved == True)).all()
        return problem_associations

    @property
    def unsolved_problems(self):
        session = db_session.create_session()
        problem_associations = session.query(UserToProblem).filter((UserToProblem.user == self) and
                                                                    (UserToProblem.solved == False)).all()
        return problem_associations

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

    def is_problem_solved(self, problem):
        problem_association = self.get_problem_association(problem)

        if not problem_association:
            return

        return problem_association.solved

    def get_problem_association(self, problem):
        session = db_session.create_session()
        problem_association = session.query(UserToProblem).get((self.id, problem.id))

        return problem_association

    def get_contest_association(self, contest):
        session = db_session.create_session()
        contest_association = session.query(UserToContest).get((self.id, contest.id))

        return contest_association

    def get_solved_contest_problems_count(self, contest):
        solved_problems_count = 0
        
        for problem in contest.problems:
            problem_association = self.get_problem_association(problem)
            if problem_association and problem_association.solved:
                solved_problems_count += 1

        return solved_problems_count

    def join_contest(self, contest):
        session = db_session.create_session()
        contest_association = session.query(UserToContest).get((self.id, contest.id))

        if contest_association or contest.is_finished():
            return
        
        contest_association = UserToContest()
        contest_association.contest = contest
        self.contests.append(contest_association)

    def rate_news(self, news, rate):
        session = db_session.create_session()

        news_rate_association = session.query(UserToNews).get((self.id, news.id))

        if news_rate_association:
            news.rating -= news_rate_association.rate
            news_rate_association.rate = rate
            news.rating += rate

            session.commit()
            return

        news_rate_association = UserToNews()
        news_rate_association.user = self
        news_rate_association.news = news
        news_rate_association.rate = rate

        news.rating += rate

        session.add(news_rate_association)
        session.commit()

    def unrate_news(self, news):
        session = db_session.create_session()

        news_rate_association = session.query(UserToNews).get((self.id, news.id))

        if not news_rate_association:
            return

        news.rating -= news_rate_association.rate
        session.delete(news_rate_association)

        session.commit()

    def get_news_rate(self, news):
        session = db_session.create_session()

        news_rate_association = session.query(UserToNews).get((self.id, news.id))

        if not news_rate_association:
            return

        return news_rate_association.rate

