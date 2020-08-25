from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class CreateNewsForm(FlaskForm):
    title = StringField('Заголовок')
    body = StringField('Тело новости', widget=TextArea())
    submit = SubmitField('Создать')
