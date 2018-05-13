from .mixin import db, Model


class Comment(Model):
    __tablename__ = 'comments'

    body_text = db.Column(db.String(200), nullable=False)
    is_enable = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeidnKey('articles.id'))

    def __init__(self, *args, **kwargs):
        super().__init(*args, **kwargs)

    def __repr__(self):
        return f'<Comment({self.name!r})>'