from functools import wraps
from threading import Thread

from flask import jsonify, request
from flask_login import current_user

from .errors import PermissionError


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
        'result': result
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
                accept_mimetypes = request.accept_mimetypes
                if accept_mimetypes.accept_json and \
                        not accept_mimetypes.accept_html:
                    return generate_error_json(PermissionError.Forbidden)
                else:
                    return jsonify('没有权限')
            return func(*args, **kwargs)
        return wrapper
    return decorator