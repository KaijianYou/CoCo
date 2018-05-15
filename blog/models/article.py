from .mixin import db, Model
from .tag import article_tags


class Article(Model):
    __tablename__ = 'articles'

    title = db.Column(db.String(64), index=True)
    body_text = db.Column(db.Text, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    is_enable = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='articles', lazy='dynamic')
    tags = db.relationship('Tag', secondary=article_tags, lazy='dynamic',
                           backref=db.backref('articles', lazy='joined'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Article({self.title!r})>'
