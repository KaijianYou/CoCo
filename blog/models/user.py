from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from .mixin import db, Model


class UserPermission:
    ADMIN = 0x1
    COMMENT = 0x2


class UserRole:
    GENERAL = 1
    ADMINISTRATOR = 2


role_permissions = {
    UserRole.GENERAL: (
        UserPermission.COMMENT
    ),
    UserRole.ADMINISTRATOR: (
        UserPermission.ADMIN |
        UserPermission.COMMENT
    )
}


class User(Model, UserMixin):
    __tablename__ = 'users'

    nickname = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar_url = db.Column(db.String(512))
    bio = db.Column(db.String(200))
    role = db.Column(db.Integer, default=UserRole.GENERAL)
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

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
        return self.is_enable

    @property
    def is_authenticated(self):
        return self.is_enable and super().is_authenticated

    def can(self, permission):
        role_permission = role_permissions.get(self.role_type, None)
        return role_permission is not None and (role_permission & permission) == permission

    @classmethod
    def query_by_email(cls, email, is_enable=None):
        query = cls.query
        if is_enable is not None:
            query = query.filter_by(is_enable=is_enable)
        return query.filter_by(email=email).first()

    @classmethod
    def query_by_email_or_nickname(cls, email, nickname, is_enable=None):
        query = cls.query
        if is_enable is not None:
            query = query.filter_by(is_enable=is_enable)
        return query.filter(or_(cls.email == email, cls.nickname == nickname)).first()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

