import os
from Pycon import permission_required, get_page_count, query_limit_page
from flask import Blueprint, render_template, abort, redirect, request
from flask_login import current_user
from data import db_session
from data.models.user import User
from forms.upload_userpic import *
from forms.assign_role import *
from werkzeug.utils import secure_filename
from Constants import *
from lib.Permissions import *
from lib.Roles import *
from lib import Roles

blueprint = Blueprint('user', __name__, template_folder='/templates/users')


@blueprint.route('/')
@permission_required(Permissions.USERS_VIEW)
def users():
    page = int(request.args.get('page', 1)) - 1

    session = db_session.create_session()

    users = session.query(User).order_by(User.id.desc())

    page_count = get_page_count(users)
    users = query_limit_page(users, page).all()

    return render_template('user/users.html', title="Пользователи", users=users, page_count=page_count)


@blueprint.route('/<int:user_id>', methods=["GET", "POST"])
@permission_required(Permissions.USER_VIEW)
def user(user_id):
    session = db_session.create_session()

    user = session.query(User).get(user_id)
    if not user:
        abort(404)

    userpic_form = UploadUserpicForm()
    if userpic_form.validate_on_submit() and (user == current_user or current_user.get_role() == AdminRole):
        file = userpic_form.image.data
        filename = secure_filename(file.filename)

        old_path = user.userpic_uri
        if old_path:
            try:
                path = APP_ROOT + old_path
                os.remove(path)
            except Exception as e:
                pass

        short_folder = "/static/img/userpics"
        short_path = os.path.join(short_folder, filename)

        path = APP_ROOT + short_path
        file.save(path)

        user.userpic_uri = short_path
        session.commit()

    assign_role_form = AssignRoleForm()
    if assign_role_form.validate_on_submit() and current_user.is_permitted(Permissions.ASSIGN_ROLES):
        user.role = assign_role_form.role.data

        session.commit()

    return render_template('user/user.html', title=f"Профиль {user.login}",
                           user=user, assign_role_form=assign_role_form, userpic_form=userpic_form)


@blueprint.route('/<int:user_id>/delete')
@permission_required(Permissions.USER_DELETE)
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)

    if not user:
        abort(404)

    session.delete(user)
    session.commit()

    return redirect('..')


@blueprint.route('/<int:user_id>/delete_userpic', methods=["GET", "POST"])
@permission_required(Permissions.USER_LOAD_USERPIC)
def user_delete_userpic(user_id):
    session = db_session.create_session()

    user = session.query(User).get(user_id)
    if not user:
        abort(404)

    if not (user == current_user or current_user.get_role() == AdminRole):
        abort(403)

    path = user.userpic_uri
    if path:
        try:
            path = APP_ROOT + path
            os.remove(path)
        except Exception as e:
            pass

    user.userpic_uri = None
    session.commit()

    return redirect(f"../{user.id}")
