from flask import Blueprint, current_app
from flask_login import login_user, logout_user, login_required

from .forms import LoginForm, RegisterForm
from blog.errors import WRONG_EMAIL_OR_PASSWORD, ILLEGAL_FORM, EMAIL_ALREADY_REGISTERED, \
    NICKNAME_ALREADY_USED
from blog.models.user import User, UserRole
from blog.utils import generate_success_json, generate_error_json


blueprint = Blueprint('auth', __name__)


@blueprint.route('/login', methods=['POST'])
def login():
    form = LoginForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(ILLEGAL_FORM)
    user = User.get_by_email(form.email.data, enabled=True)
    if user is not None and user.verify_password(form.password.data):
        login_user(user, remember=True)
        return generate_success_json()
    return generate_error_json(WRONG_EMAIL_OR_PASSWORD)


@blueprint.route('/register', methods=['POST'])
def register():
    form = RegisterForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(ILLEGAL_FORM)
    email, nickname = form.email.data, form.nickname.data
    user = User.get_by_email_or_nickname(email, nickname, enabled=True)
    if user is not None:
        if user.nickname == nickname:
            return generate_error_json(NICKNAME_ALREADY_USED)
        return generate_error_json(EMAIL_ALREADY_REGISTERED)
    if email == current_app.config['ADMIN_EMAIL']:
        role = UserRole.ADMINISTRATOR
    else:
        role = UserRole.GENERAL
    User.create(
        nickname=nickname,
        email=email,
        password=form.password.data,
        role=role
    )
    return generate_success_json()


@blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return generate_success_json()

