from flask import Blueprint, current_app, url_for
from flask_login import login_user, logout_user, login_required, current_user

from .forms import LoginForm, RegisterForm, ResetPasswordForm, RequestPasswordResetForm
from blog import errors
from blog.models.user import User, UserRole
from blog.utils import generate_success_json, generate_error_json
from blog.email_util import EmailUtil


blueprint = Blueprint('auth', __name__)


@blueprint.route('/login', methods=['POST'])
def login():
    form = LoginForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(errors.ILLEGAL_FORM)
    user = User.get_by_email(form.email.data, enabled=True)
    if user is not None and user.verify_password(form.password.data):
        login_user(user, remember=True)
        return generate_success_json()
    return generate_error_json(errors.WRONG_EMAIL_OR_PASSWORD)


@blueprint.route('/register', methods=['POST'])
def register():
    form = RegisterForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(errors.ILLEGAL_FORM)
    email, nickname = form.email.data, form.nickname.data
    user = User.get_by_email_or_nickname(email, nickname, enabled=True)
    if user is not None:
        if user.nickname == nickname:
            return generate_error_json(errors.NICKNAME_ALREADY_USED)
        return generate_error_json(errors.EMAIL_ALREADY_REGISTERED)
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


@blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return generate_success_json()


@blueprint.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return generate_error_json(errors.ALREADY_LOGIN)
    form = RequestPasswordResetForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(errors.ILLEGAL_FORM)

    user = User.get_by_email(form.email.data, enabled=True)
    if not user:
        return generate_error_json(errors.EMAIL_NOT_REGISTERED)

    token = user.get_password_reset_token()
    EmailUtil.send_password_reset_email(
        [user.email],
        user.nickname,
        url_for('auth.reset_password', token=token, _external=True)
    )
    return generate_success_json()


@blueprint.route('/reset-password/<string:token>', methods=['GET'])
def verify_password_token(token):
    if not current_user.is_anonymous:
        return generate_error_json(errors.ALREADY_LOGIN)
    user = User.verify_password_reset_token(token)
    if not user:
        return generate_error_json(errors.PASSWORD_RESET_TOKEN_INVALID)
    result = {
        'userId': user.id
    }
    return generate_success_json(result)


@blueprint.route('/users/<int:user_id>/reset-password', methods=['POST'])
def reset_password(user_id):
    if not current_user.is_anonymous:
        return generate_error_json(errors.ALREADY_LOGIN)
    user = User.get_by_id(user_id, enabled=True)
    if not user:
        return generate_error_json(errors.INTERNAL_ERROR)
    form = ResetPasswordForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(errors.ILLEGAL_FORM)
    user.update(password=form.password.data)
    return generate_success_json()

