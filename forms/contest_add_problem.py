from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class ContestAddProblemForm(FlaskForm):
    problem_id = IntegerField('ID задачи', validators=[DataRequired()])
    submit = SubmitField('Добавить')
