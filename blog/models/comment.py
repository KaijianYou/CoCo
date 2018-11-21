from datetime import timedelta

from .mixin import db, Model


class Comment(Model):
    __tablename__ = 'comment'

    body = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Comment({self.body!r})>'

    def to_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'author': self.author.nickname,
            'createDatetime': self.utc_created + timedelta(hours=8)
        }

    @classmethod
    def get_latest_by_article_id(cls, article_id, enabled=None):
        query = cls.query
        if enabled is not None:
            query = query.filter_by(enabled=enabled)
        return query.filter_by(article_id=article_id).order_by(cls.id.desc()).first()
