from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length, EqualTo

from blog.utils import PasswordRequired


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(max=32)])
    password = PasswordField(validators=[InputRequired(), PasswordRequired()])


class RegisterForm(FlaskForm):
    nickname = StringField(validators=[InputRequired(), Length(max=32)])
    email = StringField(validators=[InputRequired(), Email(), Length(max=32)])
    password = PasswordField(validators=[InputRequired(), PasswordRequired()])
    password2 = PasswordField(validators=[InputRequired(), PasswordRequired(), EqualTo('password')])

