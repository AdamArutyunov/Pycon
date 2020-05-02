import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..db_session import SqlAlchemyBase


user_to_solved_problem = Table('user_to_solved_problem', SqlAlchemyBase.metadata,
        Column('user', Integer, ForeignKey('users.id')),
        Column('solved_problem', Integer, ForeignKey('problems.id'))
)

user_to_unsolved_problem = Table('user_to_unsolved_problem', SqlAlchemyBase.metadata,
        Column('user', Integer, ForeignKey('users.id')),
        Column('unsolved_problem', Integer, ForeignKey('problems.id'))
)


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    submissions = orm.relation("Submission", back_populates='submitter')

    solved_problems = orm.relation('Problem', secondary='user_to_solved_problem',
                                   backref='users_solved')

    unsolved_problems = orm.relation('Problem', secondary='user_to_unsolved_problem',
                                   backref='users_unsolved')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


