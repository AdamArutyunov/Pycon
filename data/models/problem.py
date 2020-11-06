import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase
from .. import db_session
from .user import UserToProblem


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
        session = db_session.create_session()
        user_associations = session.query(UserToProblem).filter((UserToProblem.problem == self) &
                                                                (UserToProblem.solved == True)).all()
        return user_associations
    
    @property
    def users_unsolved(self):
        session = db_session.create_session()
        user_associations = session.query(UserToProblem).filter((UserToProblem.problem == self) &
                                                                (UserToProblem.solved == False)).all()
        return user_associations

    @property
    def examples(self):
        # Должно быть обдумано
        return list(filter(lambda x: x.example, self.tests))
