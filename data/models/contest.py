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
    
    
