import time
from datetime import datetime

import jwt
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from .mixin import db, Model
from .message import Message


class UserPermission:
    ADMIN = 0x1
    COMMENT = 0x2
    PUBLISH_ARTICLE = 0x4
    REVIEW_COMMENT = 0x8
    MESSAGE = 0x10


class UserRole:
    GENERAL = 1
    ADMINISTRATOR = 2


role_permissions = {
    UserRole.GENERAL: (
        UserPermission.COMMENT,
        UserPermission.MESSAGE
    ),
    UserRole.ADMINISTRATOR: (
        UserPermission.ADMIN |
        UserPermission.COMMENT |
        UserPermission.PUBLISH_ARTICLE |
        UserPermission.REVIEW_COMMENT |
        UserPermission.MESSAGE
    )
}


class User(Model, UserMixin):
    """用户表"""
    __tablename__ = 'users'  # 因为 PostgreSQL 内置了一张 "user" 表，所以为了区分，这里使用 "users" 表名

    nickname = db.Column(db.String(32), unique=True, nullable=False, comment='昵称')
    email = db.Column(db.String(64), unique=True, nullable=False, comment='邮箱')
    password_hash = db.Column(db.String(128), nullable=False, comment='密码')
    avatar_url = db.Column(db.String(256), comment='头像URL')
    bio = db.Column(db.String(200), comment='个人简历')
    role = db.Column(db.SmallInteger(), default=UserRole.GENERAL, comment='用户角色')
    last_message_read_time = db.Column(db.DateTime, comment='读最近一次消息的时间')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<User({self.nickname!r})>'

    def get_id(self):
        return self.id

    def update(self, **kwargs):
        if 'password' in kwargs:
            self.password = kwargs.pop('password')
        super().update(**kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.deleted

    @property
    def is_authenticated(self):
        return self.deleted and super().is_authenticated

    def can(self, permission):
        role_permission = role_permissions.get(self.role, None)
        return role_permission is not None and (role_permission & permission) == permission

    @classmethod
    def get_by_email(cls, email, deleted=None):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        return query.filter_by(email=email).first()

    @classmethod
    def get_by_email_or_nickname(cls, email, nickname, deleted=None):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        return query.filter(or_(cls.email == email, cls.nickname == nickname)).first()

    @classmethod
    def get_password_reset_token(cls, user_id, expire_in_seconds=30*60):
        return jwt.encode(
            {'reset_password': user_id, 'exp': time.time() + expire_in_seconds},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_password_reset_token(token):
        try:
            user_id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )['reset_password']
        except Exception:
            return None
        return User.get_by_id(user_id)

    def new_messages(self):
        last_message_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self)\
            .filter(Message.created_time > last_message_read_time)\
            .count()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
