import os
from flask import Flask, abort, redirect, request
from flask_login import LoginManager, current_user
from multiprocessing import Process
from functools import wraps
from data import db_session
from data.models.user import *
from SolutionChecker import SolutionChecker
from lib.Languages import *
from lib.Roles import *
from lib.Verdicts import *
from lib import Roles


app = Flask(__name__)
app.config['SECRET_KEY'] = 'pycon_pycon_secret_key'
app.config['DATABASE_URI'] = DATABASE_URI

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

PyconSolutionChecker = SolutionChecker()
PyconSolutionCheckerProcess = Process(target=PyconSolutionChecker.parse)


login_manager.anonymous_user = PyconAnonymousUser


@app.context_processor
def context_processor():
    return dict(Permissions=Permissions, Roles=Roles, VERDICTS=VERDICTS, LANGUAGES=LANGUAGES)


def permission_required(permission):
    def inner_decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            if current_user.is_permitted(permission):
                return func(*args, **kwargs)
            if not current_user.is_authenticated:
                return redirect(f"/login?next={request.path}")
            abort(403)
        return new_func
    return inner_decorator


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


if __name__ == '__main__':
    import blueprints.problem
    import blueprints.contest
    import blueprints.labour
    import blueprints.submission
    import blueprints.group
    import blueprints.news
    import blueprints.user
    import blueprints.miscellaneous
    import blueprints.api

    os.chdir(APP_ROOT)
    db_session.global_init(app.config['DATABASE_URI'])
    PyconSolutionCheckerProcess.start()

    app.register_blueprint(blueprints.problem.blueprint, url_prefix='/problems')
    app.register_blueprint(blueprints.contest.blueprint, url_prefix='/contests')
    app.register_blueprint(blueprints.labour.blueprint, url_prefix='/labours')
    app.register_blueprint(blueprints.submission.blueprint, url_prefix='/submissions')
    app.register_blueprint(blueprints.group.blueprint, url_prefix='/groups')
    app.register_blueprint(blueprints.news.blueprint, url_prefix='/news')
    app.register_blueprint(blueprints.user.blueprint, url_prefix='/users')
    app.register_blueprint(blueprints.miscellaneous.blueprint)
    app.register_blueprint(blueprints.api.blueprint, url_prefix='/api')

    app.run(port=APP_PORT, host='0.0.0.0')
