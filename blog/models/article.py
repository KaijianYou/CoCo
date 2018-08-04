from datetime import timedelta

from .mixin import db, Model, SearchableMixin
from .comment import Comment


class Article(Model, SearchableMixin):
    __tablename__ = 'article'
    __searchable__ = ['body_text', 'tags', 'title']

    title = db.Column(db.String(64), nullable=False)
    body_text = db.Column(db.Text, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    comments = db.relationship('Comment', backref='article', lazy='dynamic')

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
            'isEnabled': self.enabled,
            'createDatetime': self.utc_created + timedelta(hours=8),
            'updateDatetime': self.utc_updated + timedelta(hours=8),
            'comments': [comment.to_json() for comment in self.comments],
            'category': self.category.name,
            'tags': self.tags.split(',') if self.tags else [],
            'author': self.author.nickname
        }

    def paginate_comments(self, enabled=None, order='asc', page=1, per_page=10):
        query = self.comments
        if enabled is not None:
            query = query.filter_by(enabled=enabled)
        order_param = Comment.id.asc() if order == 'asc' else Comment.id.desc()
        return query.order_by(order_param).paginate(page, per_page)

    @classmethod
    def paginate(cls, enabled=None, order='asc', page=1, per_page=10):
        query = cls.query
        if enabled is not None:
            query = query.filter_by(enabled=enabled)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).paginate(page, per_page)

    @classmethod
    def paginate_by_tag(cls, tag, enabled=None, order='asc', page=1, per_page=10):
        query = cls.query.filter(cls.tags.like(f'%{tag}%'))
        if enabled is not None:
            query = query.filter_by(enabled=enabled)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).paginate(page, per_page)

    @classmethod
    def list_tags(cls, enabled=None, order='asc'):
        query = cls.query
        if enabled is not None:
            query = query.filter_by(enabled=enabled)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).with_entities(cls.tags).all()


db.event.listen(db.session, 'before_commit', Article.before_commit)
db.event.listen(db.session, 'after_commit', Article.after_commit)
