from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.widgets.html5 import DateTimeLocalInput
from wtforms.fields.html5 import DateTimeLocalField


class CreateContestForm(FlaskForm):
    contest_name = StringField('Название')
    start_date = DateTimeLocalField('Начало', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    duration = IntegerField('Длительность')
    hidden = BooleanField('Скрыть список задач до начала')
    submit = SubmitField('Создать')
