import sys
import datetime
from flask import Flask, render_template, abort, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from multiprocessing import Process
from functools import wraps
from data import db_session
from data.models.contest import *
from data.models.problem import *
from data.models.submission import *
from data.models.test import *
from data.models.user import *
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.submit import SubmitFileForm, SubmitTextForm
from forms.create_problem import CreateProblemForm
from forms.create_test import CreateTestForm
from forms.create_contest import CreateContestForm
from forms.contest_add_problem import ContestAddProblemForm
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


def admin_required(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        if current_user.is_admin():
            return func(*args, **kwargs)
        abort(403)
    return new_func


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('index.html', title='Pycon')


@app.errorhandler(404)
def not_found(error):
    return render_template('html_error.html', title="404", error_id="404",
                           message='Такой страницы нет! Но есть много других.')


@app.errorhandler(403)
def forbidden(error):
    return render_template('html_error.html', title="403", error_id="403",
                           message='Вам сюда нельзя!')


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
    
    return render_template('problem.html',
                           title=f"Задача №{problem_id}",
                           problem=problem,
                           submit_file_form=submit_file,
                           submit_text_form=submit_text)


@app.route('/problems/create', methods=["GET", "POST"])
@login_required
@admin_required
def create_problem():
    form = CreateProblemForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        problem = Problem()
        problem.name = form.problem_name.data
        problem.situation = form.situation.data
        problem.input_data = form.input_data.data
        problem.output_data = form.output_data.data
        problem.time_limit = int(form.time_limit.data)
        problem.memory_limit = int(form.memory_limit.data)

        session.add(problem)
        session.commit()

        return redirect(f'/problems/{problem.id}')
    
    return render_template('create_problem.html',
                           title=f"Создать задачу",
                           form=form, action="Создать")


@app.route('/problems/<int:problem_id>/edit', methods=["GET", "POST"])
@login_required
@admin_required
def edit_problem(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)

    if not problem:
        abort(404)

    form = CreateProblemForm()
    if form.validate_on_submit():
        problem.name = form.problem_name.data
        problem.situation = form.situation.data
        problem.input_data = form.input_data.data
        problem.output_data = form.output_data.data
        problem.time_limit = int(form.time_limit.data)
        problem.memory_limit = int(form.memory_limit.data)

        session.commit()
        
        return redirect(f'/problems/{problem_id}')

    form.problem_name.data = problem.name
    form.situation.data = problem.situation
    form.input_data.data = problem.input_data
    form.output_data.data = problem.output_data
    form.time_limit.data = problem.time_limit
    form.memory_limit.data = problem.memory_limit

    return render_template('create_problem.html', title=f"Редактирование задачи №{problem_id}",
                           form=form, action="Сохранить")

@app.route('/problems/<int:problem_id>/create_test', methods=["GET", "POST"])
@login_required
@admin_required
def create_test(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404)
        
    form = CreateTestForm()
    if form.validate_on_submit():
        test = Test()
        test.number = len(problem.tests) + 1
        test.input_data = form.input_data.data
        test.output_data = form.output_data.data
        test.example = form.example.data
        test.problem = problem

        session.add(test)
        session.commit()
        
        return redirect(f'/problems/{problem_id}/tests')
    return render_template('create_test.html', title="Создать тест",
                           form=form)


@app.route('/problems/<int:problem_id>/delete')
@login_required
@admin_required
def delete_problem(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404)

    session.delete(problem)
    session.commit()

    return redirect('/problems')


@app.route('/submissions')
@login_required
def submissions():
    session = db_session.create_session()
    submissions = session.query(Submission).filter(Submission.submitter == current_user)\
                  .order_by(Submission.id.desc()).all()
    return render_template('submissions.html', title="Посылки",
                           submissions=submissions)


@app.route('/problems/<int:problem_id>/submissions')
@login_required
def problem_submissions(problem_id):
    session = db_session.create_session()
    submissions = session.query(Submission).join(Problem).filter((Submission.submitter == current_user) &
                                                                 (Problem.id == problem_id))\
                  .order_by(Submission.id.desc()).all()
    return render_template('submissions.html', title=f"Посылки задачи №{problem_id}",
                           submissions=submissions)


@app.route('/problems/<int:problem_id>/tests')
@login_required
@admin_required
def problem_tests(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404)

    return render_template('problem_tests.html', title=f"Тесты проблемы №{problem_id}",
                           problem=problem)

@app.route('/problems/<int:problem_id>/tests/<int:test_id>/delete')
@login_required
@admin_required
def delete_problem_test(problem_id, test_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    test = session.query(Test).get(test_id)

    if not problem or not test:
        abort(404)

    if test in problem.tests:
        problem.tests.remove(test)

    session.commit()

    return redirect(f'/problems/{problem_id}')


@app.route('/contests/create', methods=["GET", "POST"])
@login_required
@admin_required
def create_contest():
    session = db_session.create_session()
    form = CreateContestForm()

    if form.validate_on_submit():
        contest = Contest()
        contest.name = form.contest_name.data
        contest.start_date = form.start_date.data
        contest.duration = datetime.timedelta(minutes=form.duration.data)
        contest.hidden = form.hidden.data

        session.add(contest)
        session.commit()

        return redirect(f'/contests/{contest.id}')

    return render_template('create_contest.html', title="Создать контест",
                           form=form, action="Создать")


@app.route('/contests/<int:contest_id>/add_problem', methods=["GET", "POST"])
@login_required
@admin_required
def contest_add_problem(contest_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)
    if not contest:
        abort(404)

    form = ContestAddProblemForm()
    if form.validate_on_submit():
        problem_id = form.problem_id.data
        problem = session.query(Problem).get(problem_id)
        if not problem:
            return render_template('contest_add_problem.html',
                                   title=f"Добавить задачу в контест №{contest_id}",
                                   form=form,
                                   message="Задачи с таким ID нет.")

        contest.add_problem(problem)
        session.commit()
        return redirect(f'/contests/{contest_id}')

    return render_template('contest_add_problem.html',
                           title=f"Добавить задачу в контест №{contest_id}",
                           form=form)


@app.route('/contests/<int:contest_id>/edit', methods=["GET", "POST"])
@login_required
@admin_required
def edit_contest(contest_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)
    if not contest:
        abort(404)

    form = CreateContestForm()
    if form.validate_on_submit():
        contest.name = form.contest_name.data
        contest.start_date = form.start_date.data
        contest.duration = datetime.timedelta(minutes=form.duration.data)
        contest.hidden = form.hidden.data

        session.commit()
        
        return redirect(f'/contests/{contest_id}')

    form.contest_name.data = contest.name
    form.start_date.data = contest.start_date
    form.duration.data = int(contest.duration.total_seconds() // 60)
    form.hidden.data = contest.hidden

    return render_template('create_contest.html', title=f"Редактирование контеста №{contest_id}",
                           form=form, action="Сохранить")


@app.route('/contests/<int:contest_id>/delete')
def delete_contest(contest_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)

    if not contest:
        abort(404)

    session.delete(contest)
    session.commit()

    return redirect('/contests')


@app.route('/contests')
def contests():
    session = db_session.create_session()
    contests = session.query(Contest).order_by(Contest.id.desc()).all()

    return render_template('contests.html', title="Контесты",
                           contests=contests)


@app.route('/contests/<int:contest_id>')
def contest(contest_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)
    if not contest:
        abort(404)

    return render_template('contest.html', title=f'Контест №{contest_id}',
                           contest=contest)

@app.route('/contests/<int:contest_id>/standings')
def contest_standings(contest_id):
    session = db_session.create_session()
    standings = []
    
    contest = session.query(Contest).get(contest_id)
    if not contest:
        abort(404)

    standings = sorted(contest.participants,
                       key=lambda x: -x.user.get_solved_contest_problems_count(contest))

    return render_template('standings.html', title=f"Результаты контеста №{contest_id}",
                           contest=contest, standings=standings)


@app.route('/contests/<int:contest_id>/delete_problem/<int:problem_id>')
@login_required
@admin_required
def delete_contest_problem(contest_id, problem_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)
    problem = session.query(Problem).get(problem_id)

    if not contest or not problem:
        abort(404)

    if problem in contest.problems:
        contest.problems.remove(problem)

    session.commit()
    return redirect(f'/contests/{contest_id}')
    

@app.route('/contests/<int:contest_id>/join')
@login_required
def join_contest(contest_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)
    if not contest:
        abort(404)

    current_user.join_contest(contest)
    session.commit()

    return redirect(f'/contests/{contest_id}')


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
