from functools import wraps
from threading import Thread

from flask import jsonify
from flask_login import current_user
from wtforms.validators import Regexp

from blog.errors import PERMISSION_FORBIDDEN


def async_task(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return decorator


def generate_success_json(result=None):
    result = {} if result is None else result
    data = {
        'status': 'OK',
        'data': result
    }
    return jsonify(data)


def generate_error_json(error):
    data = {
        'status': 'ERROR',
        'errorCode': error.code,
        'errorMessage': error.message
    }
    return jsonify(data)


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                return generate_error_json(PERMISSION_FORBIDDEN)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class PasswordRequired:
    def __init__(self):
        self.password_format = r'^[A-Za-z0-9_@#]{6,32}'
        self.message = '密码长度必须在6到12个字符之间，且只能出现数字、英文字母以及 _ @ # 等字符'

    def __call__(self, form, field):
        Regexp(self.password_format).__call__(form, field, self.message)

