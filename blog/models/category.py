from .mixin import db, Model


class Category(Model):
    __tablename__ = 'categories'

    name = db.Column(db.String(20), index=True, unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init(*args, **kwargs)

    def __repr__(self):
        return f'<Category({self.name!r})>'