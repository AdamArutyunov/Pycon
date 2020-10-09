import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Submission(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    submitter_id = Column(Integer, ForeignKey("users.id"))
    submitter = orm.relation("User")
    problem_id = Column(Integer, ForeignKey('problems.id'))
    problem = orm.relation("Problem")
    data = Column(String, nullable=False)
    language = Column(Integer, nullable=False)
    submit_timestamp = Column(DateTime, default=datetime.datetime.now, nullable=False)
    verdict = Column(Integer, nullable=False, default=0)
    test = Column(Integer, nullable=True)
    time = Column(Integer, nullable=True)  # Warning, time in ms!
    memory = Column(Integer, nullable=True)  # Warning, memory in KB!

    def set_verdict(self, verdict):
        self.verdict = verdict.id
        self.time = verdict.time
        self.memory = verdict.memory

    def set_current_test(self, test_number):
        self.test = test_number
    
