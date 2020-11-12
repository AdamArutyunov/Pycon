import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Labour(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'labours'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    problems = orm.relation("Problem",
                            secondary="labour_to_problem",
                            backref="labours")
    start_date = Column(DateTime, default=datetime.datetime.now, nullable=False)
    end_date = Column(DateTime, default=datetime.datetime.now, nullable=False)
    perfomance_time = Column(Interval, nullable=False)

    def is_active(self):
        if self.is_started() and not self.is_finished():
            return True
        return False

    def is_started(self):
        if self.start_date <= datetime.datetime.now():
            return True
        return False

    def is_finished(self):
        if self.end_date < datetime.datetime.now():
            return True
        return False

    def add_problem(self, problem):
        if problem in self.problems:
            return

        self.problems.append(problem)


labour_to_problem = Table('labour_to_problem', SqlAlchemyBase.metadata,
    Column('labour', Integer, ForeignKey('labours.id')),
    Column('problem', Integer, ForeignKey('problems.id'))
)
