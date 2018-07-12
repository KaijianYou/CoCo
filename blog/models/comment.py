from datetime import timedelta

from .mixin import db, Model


class Comment(Model):
    __tablename__ = 'comments'

    body_text = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Comment({self.name!r})>'

    def to_json(self):
        return {
            'id': self.id,
            'body': self.body_text,
            'authorName': self.author.nickname,
            'createDatetime': self.utc_created + timedelta(hours=8)
        }
