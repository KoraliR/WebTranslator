from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField

class LoginForm(FlaskForm):
    user = StringField('Имя пользователя')
    password = PasswordField('Пароль')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    register_btn = SubmitField('Зарегистрироваться')