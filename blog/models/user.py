from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .mixin import db, Model
from .role import Role


class User(Model, UserMixin):
    __tablename__ = 'users'

    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.Binary(128), nullable=False)
    is_enable = db.Column(db.Boolean(), default=False)
    role_id = db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))

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

    def can(self, permissions):
        role = Role.find_by_id(self.role_id)
        return role is not None and (role.permissions & permissions) == permissions


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
