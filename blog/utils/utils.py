from functools import wraps
from threading import Thread

from flask import jsonify
from flask_login import current_user

from blog.errors import PERMISSION_FORBIDDEN
from blog.utils.json_util import generate_error_json


def async_task(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return decorator


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                return generate_error_json(PERMISSION_FORBIDDEN)
            return func(*args, **kwargs)
        return wrapper
    return decorator

