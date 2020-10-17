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


assoc = session.query(UserToLabour).all()
for a in assoc:
    print(a, a.labour.name, a.user.login, a.performance_date, a.is_finished(), a.labour.duration)
session.commit()
