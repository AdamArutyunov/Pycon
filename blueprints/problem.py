from Pycon import admin_required, PyconSolutionChecker
from flask import Blueprint, render_template, abort, redirect
from flask_login import login_required, current_user
from data import db_session
from data.models.problem import Problem
from data.models.submission import Submission
from data.models.test import Test
from forms.submit import *
from forms.create_problem import *
from forms.create_test import *

blueprint = Blueprint('problem', __name__, template_folder='/templates/problem')


@blueprint.route('/')
def problems():
    session = db_session.create_session()
    problems = session.query(Problem).order_by(Problem.id.desc()).all()
    return render_template('problem/problems.html', title="Задачи",
                           problems=problems)


@blueprint.route('/<int:problem_id>', methods=["GET", "POST"])
def problem(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404)

    submit_form = SubmitForm()
    if submit_form.validate_on_submit():
        file = submit_form.data_file.data
        if file:
            PyconSolutionChecker.submit(problem, submit_form.language.data,
                                        file.read().decode(encoding='utf-8'))

            return redirect(f'/submissions')

        data = submit_form.data.data
        PyconSolutionChecker.submit(problem, submit_form.language.data,
                                    data)

        return redirect(f'/submissions')

    return render_template('problem/problem.html',
                           title=f"Задача №{problem_id}",
                           problem=problem,
                           submit_form=submit_form)


@blueprint.route('/create', methods=["GET", "POST"])
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

        return redirect(f'{problem.id}')

    return render_template('problem/create_problem.html',
                           title=f"Создать задачу",
                           form=form, action="Создать")


@blueprint.route('/<int:problem_id>/edit', methods=["GET", "POST"])
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

        return redirect(f'../{problem_id}')

    form.problem_name.data = problem.name
    form.situation.data = problem.situation
    form.input_data.data = problem.input_data
    form.output_data.data = problem.output_data
    form.time_limit.data = problem.time_limit
    form.memory_limit.data = problem.memory_limit

    return render_template('problem/create_problem.html', title=f"Редактирование задачи №{problem_id}",
                           form=form, action="Сохранить")


@blueprint.route('/<int:problem_id>/delete')
@login_required
@admin_required
def delete_problem(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404)

    session.delete(problem)
    session.commit()

    return redirect(f'..')


@blueprint.route('/<int:problem_id>/submissions')
@login_required
def problem_submissions(problem_id):
    session = db_session.create_session()
    submissions = session.query(Submission).join(Problem).filter((Submission.submitter == current_user) &
                                                                 (Problem.id == problem_id))\
                  .order_by(Submission.id.desc()).all()
    return render_template('submission/submissions.html', title=f"Посылки задачи №{problem_id}",
                           submissions=submissions)


@blueprint.route('/<int:problem_id>/tests')
@login_required
@admin_required
def problem_tests(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404)

    return render_template('problem/problem_tests.html', title=f"Тесты задачи №{problem_id}",
                           problem=problem)


@blueprint.route('/<int:problem_id>/tests/create', methods=["GET", "POST"])
@login_required
@admin_required
def problem_create_test(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404)

    form = CreateTestForm()
    if form.validate_on_submit():
        test = Test()
        test.number = len(problem.tests) + 1
        test.input_data = form.input_data.data.replace('\r', '')
        test.output_data = form.output_data.data.replace('\r', '')
        test.example = form.example.data
        test.problem = problem

        session.add(test)
        session.commit()

        return redirect(f'../tests')
    return render_template('problem/create_test.html', title="Создать тест",
                           form=form)


@blueprint.route('/<int:problem_id>/tests/<int:test_id>/edit', methods=["GET", "POST"])
@login_required
@admin_required
def problem_edit_test(problem_id, test_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    test = session.query(Test).get(test_id)

    if not problem or not test:
        abort(404)

    if test.problem is not problem:
        abort(404)

    form = CreateTestForm()
    if form.validate_on_submit():
        test.number = len(problem.tests) + 1
        test.input_data = form.input_data.data.replace('\r', '')
        test.output_data = form.output_data.data.replace('\r', '')
        test.example = form.example.data

        session.commit()

        return redirect(f'../../tests')

    form.input_data.data = test.input_data
    form.output_data.data = test.output_data
    form.example.data = test.example

    return render_template('problem/create_test.html', title="Редактировать тест",
                           form=form)


@blueprint.route('/<int:problem_id>/tests/<int:test_id>/remove')
@login_required
@admin_required
def problem_remove_test(problem_id, test_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    test = session.query(Test).get(test_id)

    if not problem or not test:
        abort(404)

    # Можно просто удалить сам тест, позднее поправлю
    if test in problem.tests:
        problem.tests.remove(test)

    session.commit()

    return redirect(f'../../tests')
