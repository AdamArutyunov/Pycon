from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class LabourAddProblemForm(FlaskForm):
    problem_id = IntegerField('ID задачи', validators=[DataRequired()])
    submit = SubmitField('Добавить')
