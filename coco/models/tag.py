from .mixin import db, Model


class Tag(Model):
    """标签表"""
    __tablename__ = 'tag'
    __table_args__ = (
        db.UniqueConstraint('author_id', 'name', 'deleted'),
    )

    author_id = db.Column(db.Integer(), nullable=False, index=True, comment='用户的ID')
    name = db.Column(db.String(10), nullable=False, unique=True, comment='名称')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Tag({self.name!r})>'
