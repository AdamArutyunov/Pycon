import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Contest(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'contests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    problems = orm.relation("Problem",
                            secondary="contest_to_problem",
                            backref="contest")
    
    
