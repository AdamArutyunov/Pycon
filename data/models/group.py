import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Group(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    users = orm.relation('User', back_populates='group')

    def add_user(self, user):
        if user in self.users:
            return
        self.users.append(user)

    def remove_user(self, user):
        if user not in self.users:
            return
        self.users.remove(user)
