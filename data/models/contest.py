import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


contest_to_problem = Table('contest_to_problem', SqlAlchemyBase.metadata,
    Column('contest', Integer, ForeignKey('contests.id')),
    Column('problem', Integer, ForeignKey('problems.id'))
)


class Contest(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'contests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    problems = orm.relation("Problem",
                            secondary="contest_to_problem",
                            backref="contests")
    start_date = Column(DateTime, default=datetime.datetime.now, nullable=False)
    duration = Column(Interval, nullable=True)
    hidden = Column(Boolean, default=True)

    def is_active(self):
        if self.is_started() and not self.is_finished():
            return True
        return False

    def is_started(self):
        if self.start_date <= datetime.datetime.now():
            return True
        return False

    def is_finished(self):
        if self.duration and datetime.datetime.now() >= self.start_date + self.duration:
            return True
        return False

    def add_problem(self, problem):
        if problem in self.problems:
            return

        self.problems.append(problem)
    
    
