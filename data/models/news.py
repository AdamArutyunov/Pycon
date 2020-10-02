import datetime
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_date = Column(DateTime, default=datetime.datetime.now)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = orm.relation("User")
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    rating = Column(Integer, nullable=True, default=0)
