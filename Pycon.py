import os
from flask import Flask, abort, redirect, request, render_template
from flask_login import LoginManager, current_user
from flask_assets import Environment, Bundle
from slimish_jinja import SlimishExtension
from multiprocessing import Process
from functools import wraps
from data import db_session
from data.models.user import *
from SolutionChecker import SolutionChecker
from lib.Languages import *
from lib.Roles import *
from lib.Verdicts import *
from lib import Roles
from math import ceil


app = Flask(__name__)
app.jinja_options['extensions'].append(SlimishExtension)

assets = Environment(app)
assets.url = "/static"
sass = Bundle("css/sass/style.sass", filters="libsass",
              output="css/new_style.css", depends='**/*.sass')
assets.register('sass', sass)

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


def get_page_count(query):
    return ceil(query.count() / PAGE_SIZE)


def query_limit_page(query, page):
    return query.offset(page * PAGE_SIZE).limit(PAGE_SIZE)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route("/article/<path:path>")
def article(path):
    try:
        return render_template(f"miscellaneous/{path}")
    except Exception as e:
        print(e)
        abort(404)


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
