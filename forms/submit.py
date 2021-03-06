from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from lib.Languages import *


class SubmitForm(FlaskForm):
    language = SelectField("Язык", coerce=int,
                           choices=list(map(lambda x: (x.id, x.display_name), LANGUAGES.values())))
    data = StringField(widget=TextArea())
    data_file = FileField()
    submit_button = SubmitField('Отправить')
