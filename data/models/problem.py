import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


association_table = Table('contest_to_problem', SqlAlchemyBase.metadata,
    Column('contest', sqlalchemy.Integer, sqlalchemy.ForeignKey('contests.id')),
    Column('problem', sqlalchemy.Integer, sqlalchemy.ForeignKey('problems.id'))
)



class Problem(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'problems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    situation = Column(String, nullable=False)
    input_data = Column(String, nullable=True)
    output_data = Column(String, nullable=True)
    examples = Column(ARRAY(Integer), nullable=True)
    solution = Column(String, nullable=False)
    tests = orm.relation("Test", back_populates='problem')
    time_limit = Column(Integer, nullable=True)
    memory_limit = Column(Integer, nullable=True)
    
    
