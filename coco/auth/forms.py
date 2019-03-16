from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length, EqualTo

from coco.utils.form_util import PasswordRequired


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(max=64)])
    password = PasswordField(validators=[InputRequired(), PasswordRequired()])


class RegisterForm(FlaskForm):
    nickname = StringField(validators=[InputRequired(), Length(max=32)])
    email = StringField(validators=[InputRequired(), Email(), Length(max=64)])
    password = PasswordField(validators=[InputRequired(), PasswordRequired()])
    password2 = PasswordField(validators=[InputRequired(), PasswordRequired(), EqualTo('password')])


class RequestPasswordResetForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(max=64)])


class ResetPasswordForm(FlaskForm):
    password = PasswordField(validators=[InputRequired(), PasswordRequired()])
    password2 = PasswordField(validators=[InputRequired(), PasswordRequired(), EqualTo('password')])

