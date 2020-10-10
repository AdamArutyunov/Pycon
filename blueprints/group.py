from Pycon import permission_required
from flask import Blueprint, render_template, abort, redirect
from flask_login import current_user
from data import db_session
from data.models.group import Group
from data.models.user import User
from forms.create_group import *
from forms.group_add_user import *
from lib.Permissions import *
from lib.Roles import *

blueprint = Blueprint('group', __name__, template_folder='/templates/group')


@blueprint.route('/')
@permission_required(Permissions.GROUPS_VIEW)
def groups():
    session = db_session.create_session()
    groups = session.query(Group).order_by(Group.id).all()
    return render_template('group/groups.html', title="Группы",
                           groups=groups)


@blueprint.route('/<int:group_id>')
@permission_required(Permissions.GROUP_VIEW)
def group(group_id):
    session = db_session.create_session()
    group = session.query(Group).get(group_id)

    if not group:
        abort(404)

    if not (current_user.group == group or current_user.get_role() == AdminRole):
        abort(403)

    return render_template('group/group.html', title=group.name, group=group)


@blueprint.route('/create', methods=["GET", "POST"])
@permission_required(Permissions.GROUP_CREATE)
def create_group():
    session = db_session.create_session()
    form = CreateGroupForm()

    if form.validate_on_submit():
        group = Group()
        group.name = form.name.data

        session.add(group)
        session.commit()

        return redirect(f'{group.id}')

    return render_template('group/create_group.html', title="Создать группу",
                           form=form, action="Создать")


@blueprint.route('/<int:group_id>/edit', methods=["GET", "POST"])
@permission_required(Permissions.GROUP_EDIT)
def edit_group(group_id):
    session = db_session.create_session()
    group = session.query(Group).get(group_id)
    if not group:
        abort(404)

    form = CreateGroupForm()
    if form.validate_on_submit():
        group.name = form.name.data

        session.commit()

        return redirect(f'../{group.id}')

    form.name.data = group.name

    return render_template('group/create_group.html', title=f'Редактирование группы "{group.name}"',
                           form=form, action="Сохранить")


@blueprint.route('/<int:group_id>/delete')
@permission_required(Permissions.GROUP_DELETE)
def delete_group(group_id):
    session = db_session.create_session()
    group = session.query(Group).get(group_id)

    if not group:
        abort(404)

    session.delete(group)
    session.commit()

    return redirect('..')


@blueprint.route('/<int:group_id>/add_user', methods=["GET", "POST"])
@permission_required(Permissions.GROUP_ADD_USER)
def group_add_user(group_id):
    session = db_session.create_session()
    group = session.query(Group).get(group_id)
    if not group:
        abort(404)

    if not (current_user.group == group or current_user.get_role() == AdminRole):
        abort(403)

    form = GroupAddUserForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        user = session.query(User).get(user_id)
        if not user:
            return render_template('group/group_add_user.html',
                                   title=f"Добавить пользователя в группу \"{group.name}\"",
                                   form=form,
                                   message="Пользователя с таким ID нет.")

        group.add_user(user)
        session.commit()
        return redirect(f'../{group_id}')

    return render_template('group/group_add_user.html',
                           title=f"Добавить пользователя в группу \"{group.name}\"",
                           form=form)


@blueprint.route('/<int:group_id>/remove_user/<int:user_id>')
@permission_required(Permissions.GROUP_REMOVE_USER)
def group_remove_user(group_id, user_id):
    session = db_session.create_session()
    group = session.query(Group).get(group_id)
    user = session.query(User).get(user_id)

    if not group or not user:
        abort(404)

    if not (current_user.group == group or current_user.get_role() == AdminRole):
        abort(403)

    group.remove_user(user)

    session.commit()
    return redirect(f'../../{group_id}')
