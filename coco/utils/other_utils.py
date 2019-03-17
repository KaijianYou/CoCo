from uuid import uuid1
from functools import wraps
from threading import Thread

from flask_login import current_user

from coco.errors import PERMISSION_FORBIDDEN
from coco.utils.json_util import gen_error_json


def async_task(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        Thread(target=func, args=args, kwargs=kwargs).start()
    return decorator


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                return gen_error_json(PERMISSION_FORBIDDEN)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def gen_slug(length=8):
    hash_value = hash(str(uuid1))
    if hash_value < 0:
        hash_value = -hash_value
    return str(hash_value)[0:length]


def page_meta_data(page, page_size, total):
    return {
        '_meta': {
            'page': page,
            'pageSize': page_size,
            'total': total
        }
    }
