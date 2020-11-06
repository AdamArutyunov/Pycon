import datetime
import csv
from Pycon import permission_required, get_page_count, query_limit_page
from flask import Blueprint, render_template, abort, redirect, send_file, request
from flask_login import current_user
from data import db_session
from data.models.problem import Problem
from data.models.contest import Contest
from forms.create_contest import *
from forms.contest_add_problem import *
from lib.Permissions import *

blueprint = Blueprint('contest', __name__, template_folder='/templates/contest')


@blueprint.route('/')
@permission_required(Permissions.CONTESTS_VIEW)
def contests():
    page = int(request.args.get('page', 1)) - 1

    session = db_session.create_session()
    contests = session.query(Contest).order_by(Contest.id.desc())

    page_count = get_page_count(contests)
    contests = query_limit_page(contests, page)

    return render_template('contest/contests.html', title="Контесты", contests=contests, page_count=page_count)


@blueprint.route('/<int:contest_id>')
@permission_required(Permissions.CONTEST_VIEW)
def contest(contest_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)
    if not contest:
        abort(404)

    return render_template('contest/contest.html', title=f'Контест №{contest_id}', contest=contest)


@blueprint.route('/create', methods=["GET", "POST"])
@permission_required(Permissions.CONTEST_CREATE)
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

        return redirect(f'{contest.id}')

    return render_template('contest/create_contest.html', title="Создать контест",
                           form=form, action="Создать")


@blueprint.route('/<int:contest_id>/edit', methods=["GET", "POST"])
@permission_required(Permissions.CONTEST_EDIT)
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

        return redirect(f'../{contest.id}')

    form.contest_name.data = contest.name
    form.start_date.data = contest.start_date
    form.duration.data = int(contest.duration.total_seconds() // 60)
    form.hidden.data = contest.hidden

    return render_template('contest/create_contest.html', title=f"Редактирование контеста №{contest_id}",
                           form=form, action="Сохранить")


@blueprint.route('/<int:contest_id>/delete')
@permission_required(Permissions.CONTEST_DELETE)
def delete_contest(contest_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)

    if not contest:
        abort(404)

    session.delete(contest)
    session.commit()

    return redirect('..')


@blueprint.route('/<int:contest_id>/add_problem', methods=["GET", "POST"])
@permission_required(Permissions.CONTEST_ADD_PROBLEM)
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
            return render_template('contest/contest_add_problem.html',
                                   title=f"Добавить задачу в контест №{contest_id}",
                                   form=form,
                                   message="Задачи с таким ID нет.")

        contest.add_problem(problem)
        session.commit()
        return redirect(f'../{contest.id}')

    return render_template('contest/contest_add_problem.html',
                           title=f"Добавить задачу в контест №{contest_id}",
                           form=form)


@blueprint.route('/<int:contest_id>/remove_problem/<int:problem_id>')
@permission_required(Permissions.CONTEST_REMOVE_PROBLEM)
def contest_remove_problem(contest_id, problem_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)
    problem = session.query(Problem).get(problem_id)

    if not contest or not problem:
        abort(404)

    if problem in contest.problems:
        contest.problems.remove(problem)

    session.commit()
    return redirect(f'../../{contest.id}')


@blueprint.route('/<int:contest_id>/join')
@permission_required(Permissions.CONTEST_JOIN)
def join_contest(contest_id):
    session = db_session.create_session()
    contest = session.query(Contest).get(contest_id)
    if not contest:
        abort(404)

    current_user.join_contest(contest)
    session.commit()

    return redirect(f'../{contest.id}')


@blueprint.route('/<int:contest_id>/standings')
@permission_required(Permissions.CONTEST_VIEW_STANDINGS)
def contest_standings(contest_id):
    session = db_session.create_session()

    contest = session.query(Contest).get(contest_id)
    if not contest:
        abort(404)

    standings = sorted(contest.participants,
                       key=lambda x: -x.user.get_solved_contest_problems_count(contest))

    return render_template('contest/standings.html', title=f"Результаты контеста №{contest_id}",
                           contest=contest, standings=standings)


@blueprint.route('/<int:contest_id>/standings/csv')
@permission_required(Permissions.CONTEST_DOWNLOAD_STANDINGS)
def contest_standings_csv(contest_id):
    session = db_session.create_session()

    contest = session.query(Contest).get(contest_id)
    if not contest:
        abort(404)

    standings = sorted(contest.participants,
                       key=lambda x: -x.user.get_solved_contest_problems_count(contest))

    data = [['', 'Логин', 'Почта', '=', *list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')[:len(contest.problems)]]]

    for i, association in enumerate(standings):
        user = association.user

        row = [i + 1, user.login, user.email,
               user.get_solved_contest_problems_count(contest)]

        for problem in contest.problems:
            upa = user.get_problem_association(problem)
            if upa:
                if upa.solved:
                    row.append('+')
                else:
                    row.append('-')
            else:
                row.append('')

        data.append(row)

    with open('temp/standings.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow(row)

    return send_file('temp/standings.csv', as_attachment=True,
                     attachment_filename=f'contest_{contest.id}_standings.csv',
                     cache_timeout=-1)