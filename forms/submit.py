from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class SubmitFileForm(FlaskForm):
    data = FileField(validators=[FileRequired()])


class SubmitTextForm(FlaskForm):
    data = StringField(widget=TextArea())
    submit = SubmitField('Отправить')
