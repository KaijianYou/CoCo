from .mixin import db, Model
from .article import Article


class Category(Model):
    __tablename__ = 'category'

    name = db.Column(db.String(20), index=True, unique=True, nullable=False)
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Category({self.name!r})>'

    def to_json(self):
        return {
            'name': self.name
        }

    def paginate_articles(self, order='asc', page=1, per_page=10):
        order_param = Article.id.asc() if order == 'asc' else Article.id.desc()
        return self.articles.order_by(order_param).paginate(page, per_page)

