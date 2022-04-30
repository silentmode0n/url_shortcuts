import imp
from flask_wtf import FlaskForm
from sqlalchemy import true

from wtforms import PasswordField
from wtforms import StringField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import EmailField

from wtforms.validators import DataRequired
from wtforms.validators import ValidationError
from wtforms.validators import EqualTo

from url_shortcuts.models import Users


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


class RegistrationForm(FlaskForm):
    name = StringField(
        'Имя',
        validators=[DataRequired('Укажите ваше имя')],
        render_kw={
            'placeholder':'введите имя',
            'autofocus': True,
            }
    )
    email = EmailField(
        'Email',
        validators=[DataRequired('Укажите ваш email адрес.')],
        render_kw={
            'placeholder':'введите адрес почты',
            }
    )
    password = PasswordField(
        'Пароль', 
        validators=[DataRequired('Необходимо ввести пароль.')],
        render_kw={
            'placeholder':'введите пароль',
            }
        )
    password2 = PasswordField(
        'Пароль еще раз', 
        validators=[DataRequired('Повторите пароль.'), EqualTo('password', message='Пароли должны совпадать.')],
        render_kw={
            'placeholder':'введите пароль повторно',
            }
        )
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пользователь с таким  email уже существует.')