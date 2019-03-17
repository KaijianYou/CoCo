import enum

from sqlalchemy_utils.types.choice import ChoiceType

from .mixin import db, Model


class LinkWeight(enum.Enum):
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5


class Link(Model):
    """友链表"""
    __tablename__ = 'link'

    title = db.Column(db.String(60), nullable=False, comment='标题')
    href = db.Column(db.String(256), nullable=False, comment='链接')
    weight = db.Column(
        db.SmallInteger(),
        ChoiceType(LinkWeight, impl=db.SmallInteger),
        nullable=False,
        default=LinkWeight.One,
        comment='权重'
    )  # 权重越高，展示位置越靠前
    creator_id = db.Column(db.Integer(), nullable=False, index=True, comment='外键，用户的ID')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Link({self.title!r})>'
