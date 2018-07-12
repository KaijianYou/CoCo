from datetime import timedelta

from .mixin import db, Model
from .comment import Comment
from .article_tag import article_tag


class Article(Model):
    __tablename__ = 'articles'

    title = db.Column(db.String(64), index=True)
    body_text = db.Column(db.Text, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='article', lazy='dynamic')
    tags = db.relationship('Tag', secondary=article_tag, lazy='dynamic',
                           backref=db.backref('articles', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Article({self.title!r})>'

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'bodyText': self.body_text,
            'viewCount': self.view_count,
            'isEnable': self.is_enable,
            'createDatetime': self.utc_created + timedelta(hours=8),
            'updateDatetime': self.utc_updated + timedelta(hours=8),
            'comments': [comment.to_json() for comment in self.comments],
            'categoryName': self.category.name,
            'tagNames': [tag.name for tag in self.tags],
            'authorName': self.author.nickname
        }

    def paginate_comments(self, is_enable=None, order='asc', page=1, per_page=10):
        query = self.comments
        if is_enable is not None:
            query = query.filter_by(is_enable=is_enable)
        order_param = Comment.id.asc() if order == 'asc' else Comment.id.desc()
        return query.order_by(order_param).paginate(page, per_page)

    @classmethod
    def paginate(cls, is_enable=None, order='asc', page=1, per_page=10):
        query = cls.query
        if is_enable is not None:
            query = query.filter_by(is_enable=is_enable)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).paginate(page, per_page)
