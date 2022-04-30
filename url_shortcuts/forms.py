import imp
from flask_wtf import FlaskForm
from sqlalchemy import true

from wtforms import PasswordField
from wtforms import StringField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import EmailField

from wtforms.validators import DataRequired


class PasswordForm(FlaskForm):
    password = PasswordField(
        'Пароль', 
        validators=[DataRequired('Необходимо ввести пароль.')],
        render_kw={
            'placeholder':'введите пароль',
            'autofocus':True
            }
        )
    submit = SubmitField('Перейти')


class LoginForm(FlaskForm):
    email = EmailField(
        'Email',
        validators=[DataRequired('Укажите ваш email адрес.')],
        render_kw={
            'placeholder':'введите адрес почты',
            'autofocus': True,
            }
    )
    password = PasswordField(
        'Пароль', 
        validators=[DataRequired('Необходимо ввести пароль.')],
        render_kw={
            'placeholder':'введите пароль',
            }
        )
    submit = SubmitField('Войти')