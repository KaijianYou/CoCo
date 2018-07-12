from .mixin import db, Model
from .article import Article
from .article_tag import ArticleTag


class Tag(Model):
    __tablename__ = 'tags'

    name = db.Column(db.String(20), index=True, unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Tag({self.name!r})>'

    def to_json(self):
        return {
            'name': self.name
        }

    def paginate_articles(self, order='asc', page=1, per_page=10):
        order_param = Article.id.asc() if order == 'asc' else Article.id.desc()
        return self.articles.order_by(order_param).paginate(page, per_page)

