from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from lib.Languages import *


class SubmitFileForm(FlaskForm):
    language = SelectField("Язык", coerce=int, choices=list(map(lambda x: (x.id, x.display_name),
                                                                language_association[1:])))
    data = FileField(validators=[FileRequired()])


class SubmitTextForm(FlaskForm):
    language = SelectField("Язык", coerce=int, choices=list(map(lambda x: (x.id, x.display_name),
                                                                language_association[1:])))
    data = StringField(widget=TextArea())
    submit = SubmitField('Отправить')
