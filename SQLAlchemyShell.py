from data import db_session
from data.models.contest import Contest
from data.models.problem import Problem
from data.models.submission import Submission
from data.models.test import Test
from data.models.user import User
from Constants import *

db_session.global_init(DATABASE_URI)
session = db_session.create_session()
submissions = session.query(Submission)
submissions.delete()
session.commit()
