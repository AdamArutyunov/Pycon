import sys
from flask import Flask, render_template, abort, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from multiprocessing import Process
from data import db_session
from data.models.contest import Contest
from data.models.problem import Problem
from data.models.submission import Submission
from data.models.test import Test
from data.models.user import User
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.submit import SubmitFileForm, SubmitTextForm
from SolutionChecker import SolutionChecker
from Constants import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'pycon_pycon_secret_key'
app.config['DATABASE_URI'] = DATABASE_URI

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


PyconSolutionChecker = SolutionChecker()
PyconSolutionCheckerProcess = Process(target=PyconSolutionChecker.parse)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('index.html', title='Pycon')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', title="404")


@app.route('/problems')
def problems():
    session = db_session.create_session()
    problems = session.query(Problem).order_by(Problem.id.desc()).all()
    return render_template('problems.html', title="Задачи",
                           problems=problems)


@app.route('/problems/<int:problem_id>', methods=["GET", "POST"])
def problem(problem_id):    
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404)

    submit_file = SubmitFileForm()
    submit_text = SubmitTextForm()
    if submit_file.validate_on_submit():
        PyconSolutionChecker.submit(problem,
                                    submit_file.data.data.read().decode(encoding='utf-8'))
        return redirect(f'/submissions')
    
    if submit_text.validate_on_submit():
        PyconSolutionChecker.submit(problem,
                                    submit_text.data.data)
        return redirect(f'/submissions')
    
    problem.examples = list(filter(lambda x: x.example, problem.tests))
    return render_template('problem.html',
                           title=f"Задача №{problem_id}",
                           problem=problem,
                           submit_file_form=submit_file,
                           submit_text_form=submit_text)


@app.route('/create_problem', methods=["GET", "POST"])
def create_problem():
    return render_template('create_problem.html',
                           title=f"Создать задачу")


@app.route('/submissions')
@login_required
def submissions():
    session = db_session.create_session()
    submissions = session.query(Submission).filter(Submission.submitter == current_user)\
                  .order_by(Submission.id.desc()).all()
    return render_template('submissions.html', title="Посылки",
                           submissions=submissions)


@app.route('/problems/<int:problem_id>/submissions')
def problem_submissions(problem_id):
    session = db_session.create_session()
    submissions = session.query(Submission).join(Problem).filter((Submission.submitter == current_user) &
                                                                 (Problem.id == problem_id))\
                  .order_by(Submission.id.desc()).all()
    return render_template('submissions.html', title=f"Посылки задачи №{problem_id}",
                           submissions=submissions)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Этот логин занят.")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Эта почта занята.")
        user = User()
        user.login = form.login.data
        user.email = form.email.data
        user.set_password(form.password.data)
        
        session.add(user)
        session.commit()

        login_user(user)
        
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter((User.email == form.login_or_email.data) |
                                          (User.login == form.login_or_email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(request.args.get('next') or '/')
        return render_template('login.html',
                               message="Неправильный логин или пароль.",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    current_user
    logout_user()
    return redirect(request.args.get('next') or '/')


if __name__ == '__main__':
    db_session.global_init(app.config['DATABASE_URI'])
    PyconSolutionCheckerProcess.start()
    app.run(port=8080, host='127.0.0.1')
