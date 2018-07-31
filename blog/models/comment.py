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

    def to_json(self):
        return {
            'id': self.id,
            'body': self.body,
            'author': self.author.nickname,
            'createDatetime': self.utc_created + timedelta(hours=8)
        }
