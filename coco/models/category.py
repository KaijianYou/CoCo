from .mixin import db, Model
from .article import Article


class Category(Model):
    """分类表"""
    __tablename__ = 'category'
    __table_args__ = (
        db.UniqueConstraint('name', 'creator_id'),
    )

    name = db.Column(db.String(20), nullable=False, comment='名称')
    is_nav = db.Column(db.Boolean(), default=False, comment='是否为导航')
    creator_id = db.Column(db.Integer(), nullable=False, index=True, comment='外键，用户的ID')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Category({self.name!r})>'

    def to_dict(self):
        return {
            'name': self.name
        }

    def paginate_articles(self, order='asc', page=1, per_page=10):
        order_param = Article.id.asc() if order == 'asc' else Article.id.desc()
        return self.articles.order_by(order_param).paginate(page, per_page)

