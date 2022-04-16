from flask_wtf import FlaskForm

from wtforms import PasswordField
from wtforms import StringField
from wtforms import BooleanField
from wtforms import SubmitField

from wtforms.validators import DataRequired


class PasswordForm(FlaskForm):
    password = PasswordField(
        'Пароль', 
        validators=[DataRequired('Необходимо ввести пароль.')],
        render_kw={'placeholder':'введите пароль','autofocus':True}
        )
    submit = SubmitField('Перейти')
