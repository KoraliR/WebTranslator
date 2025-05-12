from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp

class RegForm(FlaskForm):
    user = StringField('Имя пользователя', validators=[DataRequired(),
                                                    Length(min=6, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   Length(min=6),
                                                    Regexp(r'^\S+$'),
                                                    Regexp(r'^(?=.*\d)')])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')
    