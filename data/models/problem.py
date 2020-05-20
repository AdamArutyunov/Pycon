import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Problem(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'problems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    situation = Column(String, nullable=False)
    input_data = Column(String, nullable=True)
    output_data = Column(String, nullable=True)
    tests = orm.relation("Test", back_populates='problem')
    time_limit = Column(Integer, nullable=True)
    memory_limit = Column(Integer, nullable=True)

    @property
    def users_solved(self):
        return list(map(lambda x: x.user, filter(lambda x: x.solved, self.users)))
    
    @property
    def users_unsolved(self):
        return list(map(lambda x: x.user, filter(lambda x: not x.solved, self.users)))

    @property
    def examples(self):
        return list(filter(lambda x: x.example, self.tests))
