from subprocess import Popen
from data import db_session


class SolutionChecker:
    def __init__(self):
        self.queue = []

    def parse_solutions(self):
        session = db_session.create_session()
        
        
