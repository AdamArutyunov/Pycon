from Pycon import admin_required
from flask import Blueprint, render_template, abort, redirect
from flask_login import login_required, current_user
from data import db_session
from data.models.user import User

blueprint = Blueprint('user', __name__, template_folder='/templates/users')


@blueprint.route('/')
@login_required
@admin_required
def users():
    session = db_session.create_session()

    users = session.query(User).all()

    return render_template('user/users.html', title="Пользователи",
                           users=users)


@blueprint.route('/<int:user_id>')
def user(user_id):
    session = db_session.create_session()

    user = session.query(User).get(user_id)
    if not user:
        abort(404)

    return render_template('user/user.html', title=f"Профиль {user.login}",
                           user=user)


@blueprint.route('/<int:user_id>/delete')
@login_required
@admin_required
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)

    if not user:
        abort(404)

    session.delete(user)
    session.commit()

    return redirect('..')
