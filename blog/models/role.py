from .mixin import db, Model


class Permission:
    ADMIN = 0x01  # 管理员


class Role(Model):
    __tablename__ = 'roles'

    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def __repr__(self):
        return f'<Role({self.name!r})>'

    @classmethod
    def insert_roles(cls):
        roles = {
            'Administrator': (Permission.ADMIN)
        }
        for name, permissions in roles.items():
            role = Role.query.filter_by(name=name).first()
            if role is not None:
                if role.permissions != permissions:
                    role.update(permissions=permissions)
            else:
                role.create(name, permissions)
