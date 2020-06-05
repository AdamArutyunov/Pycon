import datetime
from data import db_session
from data.models.contest import Contest
from data.models.problem import Problem
from data.models.submission import Submission
from data.models.test import Test
from data.models.user import *
from Constants import *

db_session.global_init(DATABASE_URI)
session = db_session.create_session()


u = session.query(Test).get(25)
print(repr(u.input_data))

session.commit()
