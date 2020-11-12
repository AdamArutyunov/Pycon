import datetime
import csv
from Pycon import permission_required, get_page_count, query_limit_page
from flask import Blueprint, render_template, abort, redirect, send_file, request
from flask_login import current_user
from data import db_session
from data.models.problem import Problem
from data.models.labour import Labour
from forms.create_labour import *
from forms.labour_add_problem import *
from lib.Permissions import *

blueprint = Blueprint('labour', __name__, template_folder='/templates/labour')


@blueprint.route('/')
@permission_required(Permissions.LABOURS_VIEW)
def labours():
    page = int(request.args.get('page', 1)) - 1

    session = db_session.create_session()
    labours = session.query(Labour).order_by(Labour.id.desc())

    page_count = get_page_count(labours)
    labours = query_limit_page(labours, page).all()

    return render_template('labour/labours.html', title="Работы", labours=labours, page_count=page_count)


@blueprint.route('/<int:labour_id>')
@permission_required(Permissions.LABOUR_VIEW)
def labour(labour_id):
    session = db_session.create_session()
    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    return render_template('labour/labour.html', title=f'Работа №{labour_id}', labour=labour)


@blueprint.route('/create', methods=["GET", "POST"])
@permission_required(Permissions.LABOUR_CREATE)
def create_labour():
    session = db_session.create_session()
    form = CreateLabourForm()

    if form.validate_on_submit():
        labour = Labour()
        labour.name = form.labour_name.data
        labour.start_date = form.start_date.data
        labour.end_date = form.end_date.data
        labour.perfomance_time = datetime.timedelta(minutes=form.perfomance_time.data)

        session.add(labour)
        session.commit()

        return redirect(f'{labour.id}')

    return render_template('labour/create_labour.html', title="Создать работу",
                           form=form, action="Создать")


@blueprint.route('/<int:labour_id>/edit', methods=["GET", "POST"])
@permission_required(Permissions.LABOUR_EDIT)
def edit_labour(labour_id):
    session = db_session.create_session()
    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    form = CreateLabourForm()
    if form.validate_on_submit():
        labour.name = form.labour_name.data
        labour.start_date = form.start_date.data
        labour.end_date = form.end_date.data
        labour.perfomance_time = datetime.timedelta(minutes=form.perfomance_time.data)

        session.commit()

        return redirect(f'../{labour.id}')

    form.labour_name.data = labour.name
    form.start_date.data = labour.start_date
    form.end_date.data = labour.end_date
    form.perfomance_time.data = int(labour.perfomance_time.total_seconds() // 60)

    return render_template('labour/create_labour.html', title=f"Редактирование работы №{labour_id}",
                           form=form, action="Сохранить")


@blueprint.route('/<int:labour_id>/delete')
@permission_required(Permissions.LABOUR_DELETE)
def delete_labour(labour_id):
    session = db_session.create_session()
    labour = session.query(Labour).get(labour_id)

    if not labour:
        abort(404)

    session.delete(labour)
    session.commit()

    return redirect('..')


@blueprint.route('/<int:labour_id>/add_problem', methods=["GET", "POST"])
@permission_required(Permissions.LABOUR_ADD_PROBLEM)
def labour_add_problem(labour_id):
    session = db_session.create_session()
    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    form = LabourAddProblemForm()
    if form.validate_on_submit():
        problem_id = form.problem_id.data
        problem = session.query(Problem).get(problem_id)
        if not problem:
            return render_template('labour/labour_add_problem.html',
                                   title=f"Добавить задачу в работу №{labour_id}",
                                   form=form,
                                   message="Задачи с таким ID нет.")

        labour.add_problem(problem)
        session.commit()
        return redirect(f'../{labour.id}')

    return render_template('labour/labour_add_problem.html',
                           title=f"Добавить задачу в работу №{labour_id}",
                           form=form)


@blueprint.route('/<int:labour_id>/remove_problem/<int:problem_id>')
@permission_required(Permissions.LABOUR_REMOVE_PROBLEM)
def labour_remove_problem(labour_id, problem_id):
    session = db_session.create_session()
    labour = session.query(Labour).get(labour_id)
    problem = session.query(Problem).get(problem_id)

    if not labour or not problem:
        abort(404)

    if problem in labour.problems:
        labour.problems.remove(problem)

    session.commit()
    return redirect(f'../../{labour.id}')


@blueprint.route('/<int:labour_id>/perform')
@permission_required(Permissions.LABOUR_PERFORM)
def perform_labour(labour_id):
    session = db_session.create_session()
    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    current_user.perform_labour(labour)
    session.commit()

    return redirect(f'../{labour.id}')


@blueprint.route('/<int:labour_id>/results')
@permission_required(Permissions.LABOUR_VIEW_RESULTS)
def labour_results(labour_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)

    results = sorted(labour.performers,
                     key=lambda x: -x.user.get_solved_labour_problems_count(labour))

    return render_template('labour/results.html', title=f"Результаты работы №{labour_id}",
                           labour=labour, results=results)


@blueprint.route('/<int:labour_id>/results/csv')
@permission_required(Permissions.LABOUR_DOWNLOAD_RESULTS)
def labour_results_csv(labour_id):
    session = db_session.create_session()

    labour = session.query(Labour).get(labour_id)
    if not labour:
        abort(404)


    results = sorted(labour.performers,
                     key=lambda x: -x.user.get_solved_labour_problems_count(labour))

    data = [['', 'Логин', 'Почта', '=', *list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')[:len(labour.problems)]]]

    for i, association in enumerate(results):
        user = association.user

        row = [i + 1, user.login, user.email,
               user.get_solved_labour_problems_count(labour)]

        for problem in labour.problems:
            upa = user.get_problem_association(problem)
            if upa:
                if upa.solved:
                    row.append('+')
                else:
                    row.append('-')
            else:
                row.append('')

        data.append(row)

    with open('temp/results.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow(row)

    return send_file('temp/results.csv', as_attachment=True,
                     attachment_filename=f'labour_{labour.id}_results.csv',
                     cache_timeout=-1)