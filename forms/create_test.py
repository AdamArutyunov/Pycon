from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class CreateTestForm(FlaskForm):
    input_data = StringField('Входные данные', widget=TextArea())
    output_data = StringField('Выходные данные', widget=TextArea())
    example = BooleanField('Пример')
    submit = SubmitField('Создать')
