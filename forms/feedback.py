from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class FeedbackForm(FlaskForm):
    body = StringField("Суть", widget=TextArea(), validators=[DataRequired()])
    response_contact = StringField("Контакт для связи")
    submit = SubmitField('Отправить')
