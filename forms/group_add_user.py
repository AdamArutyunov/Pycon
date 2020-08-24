from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class GroupAddUserForm(FlaskForm):
    user_id = IntegerField('ID пользователя', validators=[DataRequired()])
    submit = SubmitField('Добавить')
