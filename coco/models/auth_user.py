import time
from datetime import datetime

import jwt
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from .mixin import db, Model


class UserGroupPermission:
    All = 0x1
    WriteComment = 0x2


class UserGroup:
    Admin = 1
    Visitor = 2


GROUP_PERMISSIONS = {
    UserGroup.Visitor: (
        UserGroupPermission.WriteComment,
    ),
    UserGroup.Admin: (
        UserGroupPermission.All,
    ),
}


class AuthUser(Model, UserMixin):
    """用户表"""
    __tablename__ = 'auth_user'

    username = db.Column(db.String(32), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(254), unique=True, nullable=False, comment='邮箱')  # 254 这个限制源自 RFC3696
    password_hash = db.Column(db.String(128), nullable=False, comment='密码')
    avatar_url = db.Column(db.String(256), default='', comment='头像URL')
    bio = db.Column(db.String(200), default='', comment='个人简介')
    group = db.Column(db.SmallInteger(), comment='用户组')
    last_login_time = db.Column(db.DateTime(False), nullable=False, default=datetime.utcnow, comment='上次登录时间')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<AuthUser({self.nickname!r})>'

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
        return not self.deleted

    @property
    def is_authenticated(self):
        return self.is_active and super().is_authenticated

    def can(self, permission):
        group_permission = GROUP_PERMISSIONS.get(self.group, 0)
        return (group_permission & permission) == permission

    def update_last_login_time(self):
        self.last_login_time = datetime.utcnow()

    @classmethod
    def get_by_email(cls, email, deleted=None):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        return query.filter_by(email=email).first()

    @classmethod
    def get_by_email_or_username(cls, email, username, deleted=None):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        return query.filter(or_(cls.email == email, cls.username == username)).first()

    @classmethod
    def get_by_username(cls, username, deleted=None):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        return query.filter_by(username=username).first()

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
        return AuthUser.get_by_id(user_id)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
