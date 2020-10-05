from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed


class UploadUserpicForm(FlaskForm):
    image = FileField("Загрузить юзерпик", validators=[FileRequired(),
                                                       FileAllowed(['jpg', 'png', 'gif'],
                                                                   "Допускаются форматы .jpg, .png и .gif.")])
