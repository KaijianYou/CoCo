from .mixin import db, Model


class ArticleTag:
    def __init__(self, tag_id, article_id):
        self.tag_id = tag_id
        self.article_id = article_id


article_tag = db.Table(
    'article_tag',
    db.metadata,
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True)
)


db.mapper(ArticleTag, article_tag)

