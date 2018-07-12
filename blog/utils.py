from functools import wraps
from threading import Thread
from random import randint

from flask import jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from wtforms.validators import Regexp
from faker import Faker

from blog.models.mixin import db
from blog.models.user import User, UserRole
from blog.models.article import Article
from blog.models.category import Category
from blog.models.tag import Tag
from blog.models.comment import Comment
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


def generate_fake_data(model, seed=None, total=10):
    """使用 Faker 生成虚拟数据"""
    fake = Faker()
    if seed is not None:
        fake.seed(seed)
    count = 0
    while count < total:
        try:
            if model == User:
                user_profile = fake.profile()
                User.create(
                    nickname=user_profile['username'],
                    email=user_profile['mail'],
                    password=fake.word(ext_word_list=None),
                    avatar_url=user_profile['website'][0],
                    bio=fake.text(max_nb_chars=200),
                    role=UserRole.GENERAL
                )
            elif model == Category:
                Category.create(name=fake.word(ext_word_list=None))
            elif model == Tag:
                Tag.create(name=fake.word(ext_word_list=None))
            elif model == Comment:
                user_count = User.query.count()
                article_count = Article.query.count()
                author = User.query.offset(randint(0, user_count - 1)).first()
                article = Article.query.offset(randint(0, article_count - 1)).first()
                Comment.create(
                    body_text=fake.text(max_nb_chars=200, ext_word_list=None),
                    author=author,
                    article=article)
            elif model == Article:
                user_count = User.query.count()
                category_count = Category.query.count()
                tag_count = Category.query.count()
                author = User.query.offset(randint(0, user_count - 1)).first()
                category = Category.query.offset(randint(0, category_count - 1)).first()
                tags = Tag.query.offset(randint(0, tag_count - 1)).limit(randint(1, 5)).all()
                Article.create(
                    title=fake.text(max_nb_chars=64),
                    body_text=fake.paragraphs(nb=randint(1, 10), ext_word_list=None),
                    view_count=randint(0, 100),
                    author=author,
                    category=category,
                    tags=tags
                )
        except IntegrityError:
            db.session.rollback()
        else:
            count += 1


class PasswordRequired:
    def __init__(self):
        self.password_format = r'^[A-Za-z0-9_@#]{6,32}'
        self.message = '密码长度必须在6到12个字符之间，且只能出现数字、英文字母以及 _ @ # 等字符'

    def __call__(self, form, field):
        Regexp(self.password_format).__call__(form, field, self.message)

