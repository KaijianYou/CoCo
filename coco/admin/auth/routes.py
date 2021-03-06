from flask import Blueprint, url_for
from flask_login import login_user, logout_user, login_required, current_user

from coco import errors
from coco.models.auth_user import AuthUser
from coco.utils.json_util import gen_success_json, gen_error_json
from coco.utils.email_util import EmailUtil
from .forms import LoginForm, ResetPasswordForm, RequestPasswordResetForm


blueprint = Blueprint('admin_auth', __name__)


@blueprint.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_login_time()


@blueprint.route('/login', methods=['POST'])
def login():
    form = LoginForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return gen_error_json(errors.ILLEGAL_FORM)
    user = AuthUser.get_by_email(form.email.data, deleted=False)
    if user is not None and user.verify_password(form.password.data):
        login_user(user, remember=True)
        return gen_success_json()
    return gen_error_json(errors.WRONG_EMAIL_OR_PASSWORD)


@blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return gen_success_json()


@blueprint.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return gen_error_json(errors.ALREADY_LOGIN)
    form = RequestPasswordResetForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return gen_error_json(errors.ILLEGAL_FORM)

    user = AuthUser.get_by_email(form.email.data, deleted=False)
    if not user:
        return gen_error_json(errors.EMAIL_NOT_REGISTERED)

    # token = user.get_password_reset_token()
    token = AuthUser.get_password_reset_token(user.id)
    EmailUtil.send_password_reset_email(
        [user.email],
        user.nickname,
        url_for('auth.verify_password_token', token=token, _external=True)
    )
    return gen_success_json()


@blueprint.route('/reset-password/<string:token>', methods=['GET'])
def verify_password_token(token):
    if not current_user.is_anonymous:
        return gen_error_json(errors.ALREADY_LOGIN)
    user = AuthUser.verify_password_reset_token(token)
    if not user:
        return gen_error_json(errors.PASSWORD_RESET_TOKEN_INVALID)
    result = {
        'userId': user.id
    }
    return gen_success_json(result)


@blueprint.route('/users/<int:user_id>/reset-password', methods=['POST'])
def reset_password(user_id):
    if not current_user.is_anonymous:
        return gen_error_json(errors.ALREADY_LOGIN)
    user = AuthUser.get_by_id(user_id, deleted=False)
    if not user:
        return gen_error_json(errors.INTERNAL_ERROR)
    form = ResetPasswordForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return gen_error_json(errors.ILLEGAL_FORM)
    user.update(password=form.password.data)
    return gen_success_json()

