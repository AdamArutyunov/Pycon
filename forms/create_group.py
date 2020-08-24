from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class CreateGroupForm(FlaskForm):
    name = StringField('Название')
    submit = SubmitField('Создать')
