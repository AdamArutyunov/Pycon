import datetime
from data import db_session
from data.models.contest import Contest
from data.models.problem import Problem
from data.models.submission import Submission
from data.models.test import Test
from data.models.user import *
from data.models.group import Group
from Constants import *

db_session.global_init(DATABASE_URI)
session = db_session.create_session()


u = session.query(User).get(3)
print(u.login, u.group.name)

session.commit()
