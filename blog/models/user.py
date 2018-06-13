from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .mixin import db, Model


class UserPermission:
    ADMIN = 0x1
    COMMENT = 0x2
    UP_DOWN_VOTE = 0x4


class UserRole:
    General = 1
    ADMINISTRATOR = 2


role_permissions = {
    UserRole.General: (
        UserPermission.COMMENT |
        UserPermission.UP_DOWN_VOTE
    ),
    UserRole.ADMINISTRATOR: (
        UserPermission.ADMIN |
        UserPermission.COMMENT |
        UserPermission.UP_DOWN_VOTE
    )
}


class User(Model, UserMixin):
    __tablename__ = 'users'

    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.Binary(128), nullable=False)
    is_enable = db.Column(db.Boolean(), default=False)
    role = db.Column(db.Integer, default=UserRole.General)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<User({self.username!r})>'

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


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
