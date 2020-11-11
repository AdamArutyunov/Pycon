from Pycon import permission_required, get_page_count, query_limit_page
from flask import Blueprint, render_template, abort, request, redirect
from flask_login import current_user
from data import db_session
from data.models.submission import Submission
from data.models.user import User
from data.models.problem import *
from forms.submit import *
from lib.Verdicts import *
from lib.Permissions import *

blueprint = Blueprint('submission', __name__, template_folder='/templates/submission')


@blueprint.route('/')
@permission_required(Permissions.SUBMISSIONS_VIEW)
def submissions():
    page = int(request.args.get('page', 1)) - 1

    session = db_session.create_session()
    submissions = session.query(Submission).filter(Submission.submitter == current_user)\
                  .order_by(Submission.id.desc())

    page_count = get_page_count(submissions)
    submissions = query_limit_page(submissions, page).all()

    return render_template('submission/submissions.html', title="Посылки",
                           submissions=submissions, page_count=page_count)


@blueprint.route('/all')
@permission_required(Permissions.SUBMISSIONS_VIEW_ALL)
def submissions_all():
    session = db_session.create_session()
    submissions = session.query(Submission)

    user_id = request.args.get('user_id', None)
    page = int(request.args.get('page', 1)) - 1
    user = None

    if user_id:
        user = session.query(User).get(user_id)

    if user:
        submissions = submissions.filter(Submission.submitter == user)

    problem_id = request.args.get('problem_id', None)
    problem = None
    if problem_id:
        problem = session.query(Problem).get(problem_id)

    if problem:
        submissions = submissions.filter(Submission.problem == problem)

    submissions = submissions.order_by(Submission.id.desc())
    page_count = get_page_count(submissions)
    submissions = query_limit_page(submissions, page).all()
    
    return render_template('submission/submissions.html', title="Все посылки",
                           submissions=submissions, page_count=page_count)


@blueprint.route('/<int:submission_id>')
@permission_required(Permissions.SUBMISSION_VIEW)
def submission(submission_id):
    session = db_session.create_session()

    submission = session.query(Submission).get(submission_id)
    if not submission:
        abort(404)

    if submission.submitter != current_user and not current_user.is_permitted(Permissions.SUBMISSIONS_VIEW_ALL):
        abort(403)

    return render_template('submission/submission.html', title=f"Посылка №{submission.id}",
                           submission=submission)


@blueprint.route('/<int:submission_id>/recheck')
@permission_required(Permissions.SUBMISSION_SET_VERDICT)
def submission_recheck(submission_id):
    session = db_session.create_session()

    submission = session.query(Submission).get(submission_id)
    if not submission:
        abort(404)

    submission.verdict = 0
    session.commit()

    return redirect(f"../{submission.id}")