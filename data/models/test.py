import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Test(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer, nullable=False)
    input_data = Column(String, nullable=True)
    output_data = Column(String, nullable=True)
    example = Column(Boolean, nullable=False)
    problem_id = Column(Integer, ForeignKey('problems.id'))
    problem = orm.relation("Problem")
    
