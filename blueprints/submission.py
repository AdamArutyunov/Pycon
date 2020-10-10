from Pycon import permission_required
from flask import Blueprint, render_template, abort
from flask_login import current_user
from data import db_session
from data.models.submission import Submission
from forms.submit import *
from lib.Verdicts import *
from lib.Permissions import *

blueprint = Blueprint('submission', __name__, template_folder='/templates/submission')


@blueprint.route('/')
@permission_required(Permissions.SUBMISSIONS_VIEW)
def submissions():
    session = db_session.create_session()
    submissions = session.query(Submission).filter(Submission.submitter == current_user)\
                  .order_by(Submission.id.desc()).all()
    return render_template('submission/submissions.html', title="Посылки",
                           submissions=submissions, VERDICTS=VERDICTS)


@blueprint.route('/all')
@permission_required(Permissions.SUBMISSIONS_VIEW_ALL)
def submissions_all():
    session = db_session.create_session()
    submissions = session.query(Submission).order_by(Submission.id.desc()).all()
    
    return render_template('submission/submissions.html', title="Все посылки",
                           submissions=submissions, VERDICTS=VERDICTS)


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
                           submission=submission, LANGUAGES=LANGUAGES, VERDICTS=VERDICTS)
