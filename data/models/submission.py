import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Submission(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    submitter = orm.relation("User")
    problem = orm.relation("Problem")
    data = Column(String, nullable=False)
    verdict = Column(String, nullable=True)
    time = Column(Integer, nullable=True)
    memory = Column(Integer, nullable=True)
    submit_timestamp = Column(Integer, nullable=False)
    test_timestamp = Column(Integer, nullable=True)
    
    
