from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class CreateProblemForm(FlaskForm):
    problem_name = StringField('Название')
    time_limit = IntegerField()
    memory_limit = IntegerField()
    situation = StringField('Условие', validators=[DataRequired()], widget=TextArea())
    input_data = StringField('Входные данные', widget=TextArea())
    output_data = StringField('Выходные данные', widget=TextArea())
    submit = SubmitField('Создать')
