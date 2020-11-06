import datetime
from data import db_session
from data.models.contest import Contest
from data.models.problem import Problem
from data.models.submission import Submission
from data.models.test import Test
from data.models.user import *
from data.models.group import Group
from data.models.news import *
from Constants import *
from lib.Roles import *

db_session.global_init(DATABASE_URI)
session = db_session.create_session()

u = session.query(User).get(1)
assoc = session.query(UserToProblem).filter(UserToProblem.user == u).all()

for a in assoc:
    print(a.problem.name, a.user.login, a.solved)

for assoc in u.solved_problems:
    print(assoc.problem.name)
session.commit()
