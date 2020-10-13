from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from lib.Roles import *


class AssignRoleForm(FlaskForm):
    role = SelectField("Роль", coerce=int,
                       choices=list(map(lambda x: (x.id, x.display_name), ROLES[1:])))
    submit = SubmitField('Назначить')
