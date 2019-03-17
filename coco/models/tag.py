import enum

from .mixin import db, Model


class Tag(Model):
    """标签表"""
    __tablename__ = 'tag'
    __table_args__ = (
        db.UniqueConstraint('name', 'creator_id'),
    )

    name = db.Column(db.String(10), nullable=False, comment='名称')
    creator_id = db.Column(db.Integer(), nullable=False, index=True, comment='用户的ID')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Tag({self.name!r})>'
