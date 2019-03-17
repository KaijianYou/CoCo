import enum
from datetime import timedelta

from sqlalchemy_utils.types.choice import ChoiceType

from coco.utils.other_utils import gen_slug
from .mixin import db, Model, SearchableMixin
from .comment import Comment


class ArticleStatus(enum.Enum):
    Normal = 1
    Draft = 2


ArticleStatus.Normal.label = '正常'
ArticleStatus.Draft.label = '草稿'


class Article(Model, SearchableMixin):
    """文章表"""
    __tablename__ = 'article'
    __searchable__ = ['body_text', 'tags', 'title']

    slug = db.Column(db.String(16), index=True, nullable=False, unique=True, comment='Slug')
    title = db.Column(db.String(200), nullable=False, comment='标题')
    summary = db.Column(db.String(200), comment='摘要')
    content = db.Column(db.Text, nullable=False, comment='正文')  # 正文必须用 Markdown 格式书写
    status = db.Column(
        db.SmallInteger(),
        ChoiceType(ArticleStatus, impl=db.SmallInteger),
        nullable=False,
        default=ArticleStatus.Normal,
        comment='状态'
    )
    view_count = db.Column(db.Integer(), nullable=False, default=0, comment='浏览数')
    category_id = db.Column(db.SmallInteger(), nullable=False, index=True, comment='外键，分类的ID')
    author_id = db.Column(db.Integer(), nullable=False, index=True, comment='外键，用户的ID')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slug = self.gen_slug()

    @classmethod
    def gen_slug(cls):
        while True:
            temp_slug = gen_slug()
            obj = cls.get_by_slug(slug=temp_slug)
            if not obj:
                return temp_slug

    def __repr__(self):
        return f'<Article({self.title!r})>'

    def to_dict(self):
        return {
            'slug': self.slug,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'viewCount': self.view_count,
            'deleted': self.deleted,
            'createTime': self.created_time + timedelta(hours=8),
            'updateTime': self.updated_time + timedelta(hours=8)
        }

    def paginate_comments(self, deleted=None, order='asc', page=1, per_page=10):
        query = self.comments
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        order_param = Comment.id.asc() if order == 'asc' else Comment.id.desc()
        return query.order_by(order_param).paginate(page, per_page)

    @classmethod
    def paginate(cls, deleted=None, order='asc', page=1, per_page=10):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).paginate(page, per_page)

    @classmethod
    def paginate_by_tag(cls, tag, deleted=None, order='asc', page=1, per_page=10):
        query = cls.query.filter(cls.tags.like(f'%{tag}%'))
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).paginate(page, per_page)

    @classmethod
    def get_by_slug(cls, slug, deleted=None):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        return query.filter_by(slug=slug).first()

    @classmethod
    def list_tags(cls, deleted=None, order='asc'):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).with_entities(cls.tags).all()

    @classmethod
    def get_by_title(cls, title, deleted=None):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        return query.filter_by(title=title).first()


db.event.listen(db.session, 'before_commit', Article.before_commit)
db.event.listen(db.session, 'after_commit', Article.after_commit)
