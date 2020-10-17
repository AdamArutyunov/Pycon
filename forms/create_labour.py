from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateTimeLocalField


class CreateLabourForm(FlaskForm):
    labour_name = StringField('Название')
    start_date = DateTimeLocalField('Начало', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    duration = IntegerField('Длительность')
    perfomance_time = IntegerField('Время на решение')
    submit = SubmitField('Создать')
