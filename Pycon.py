import os
import datetime
from flask import Flask, render_template, abort, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from multiprocessing import Process
from functools import wraps
from data import db_session
from data.models.group import *
from data.models.user import *
from data.models.news import *
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.feedback import *
from SolutionChecker import SolutionChecker
from lib.Languages import *
from lib.Permissions import *
from lib.Roles import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'pycon_pycon_secret_key'
app.config['DATABASE_URI'] = DATABASE_URI

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

PyconSolutionChecker = SolutionChecker()
PyconSolutionCheckerProcess = Process(target=PyconSolutionChecker.parse)


class PyconAnonymousUser:
    @property
    def is_active(self):
        return False

    @property
    def is_authenticated(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return None

    def get_role(self):
        return ObserverRole

    def is_permitted(self, permission):
        return self.get_role().is_permitted(permission)


login_manager.anonymous_user = PyconAnonymousUser


def admin_required(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        if current_user.is_admin():
            return func(*args, **kwargs)
        abort(403)
    return new_func


def permission_required(permission):
    def inner_decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            if current_user.is_permitted(permission):
                return func(*args, **kwargs)
            if not current_user.is_authenticated:
                return redirect("/login")
            abort(403)
        return new_func
    return inner_decorator


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
@permission_required(Permissions.INDEX_VIEW)
def index():
    session = db_session.create_session()
    news = session.query(News).order_by(News.publication_date.desc()).all()

    return render_template('index.html', title='Pycon', news=news)


@app.errorhandler(404)
def not_found(error):
    return render_template('html_error.html', title="404", error_id="404",
                           message='Такой страницы нет! Но есть много других.')


@app.errorhandler(403)
def forbidden(error):
    return render_template('html_error.html', title="403", error_id="403",
                           message='Вам сюда нельзя!')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    session = db_session.create_session()
    form.group.choices += [(group.id, group.name) for group in session.query(Group).all()]

    if form.validate_on_submit():
        if session.query(User).filter(User.login == form.login.data).first():
            return render_template('user/register.html', title='Регистрация',
                                   form=form,
                                   message="Этот логин занят.")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('user/register.html', title='Регистрация',
                                   form=form,
                                   message="Эта почта занята.")
        user = User()
        user.login = form.login.data
        user.email = form.email.data
        user.group = session.query(Group).get(form.group.data)
        user.set_password(form.password.data)
        
        session.add(user)
        session.commit()

        login_user(user)
        
        return redirect('/')

    return render_template('user/register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter((User.email == form.login_or_email.data) |
                                          (User.login == form.login_or_email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data, duration=datetime.timedelta(days=7))
            return redirect(request.args.get('next') or '/')
        return render_template('user/login.html',
                               message="Неправильный логин или пароль.",
                               form=form)

    return render_template('user/login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next') or '/')


@app.route('/feedback', methods=["GET", "POST"])
@permission_required(Permissions.FEEDBACK_LEAVE)
def feedback():
    form = FeedbackForm()

    if form.validate_on_submit():
        body = form.body.data
        contact = form.response_contact.data
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        message = ""
        message += "От: " + (current_user.login if current_user.is_authenticated else "аноним") + "\n\n"
        message += body + "\n\n"

        if contact:
            message += "Контакт для связи: " + contact

        with open(f"temp/feedback/feedback_{timestamp}.txt", "w") as f:
            f.write(message)

        return redirect("/")

    return render_template("feedback.html", title="Обратная связь", form=form)


if __name__ == '__main__':
    import blueprints.problem
    import blueprints.contest
    import blueprints.submission
    import blueprints.group
    import blueprints.news
    import blueprints.user
    import blueprints.api

    os.chdir(APP_ROOT)
    db_session.global_init(app.config['DATABASE_URI'])
    PyconSolutionCheckerProcess.start()

    app.register_blueprint(blueprints.problem.blueprint, url_prefix='/problems')
    app.register_blueprint(blueprints.contest.blueprint, url_prefix='/contests')
    app.register_blueprint(blueprints.submission.blueprint, url_prefix='/submissions')
    app.register_blueprint(blueprints.group.blueprint, url_prefix='/groups')
    app.register_blueprint(blueprints.news.blueprint, url_prefix='/news')
    app.register_blueprint(blueprints.user.blueprint, url_prefix='/users')
    app.register_blueprint(blueprints.api.blueprint, url_prefix='/api')

    app.run(port=APP_PORT, host='0.0.0.0')
