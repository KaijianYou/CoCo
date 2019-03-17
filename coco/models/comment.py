from datetime import timedelta

from .mixin import db, Model


class Comment(Model):
    """评论表"""
    __tablename__ = 'comment'

    article_id = db.Column(db.SmallInteger(), nullable=False, index=True, comment='外键，文章的ID')
    nickname = db.Column(db.String(50), nullable=False, comment='昵称')
    content = db.Column(db.String(200), nullable=False, comment='内容')
    website = db.Column(db.String(256), comment='网站')
    email = db.Column(db.String(254), nullable=False, comment='邮箱')  # 254 这个限制源自 RFC3696

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Comment({self.content!r})>'

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'createTime': self.created_time + timedelta(hours=8)
        }

    @classmethod
    def get_latest_by_article_id(cls, article_id, deleted=None):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        return query.filter_by(article_id=article_id).order_by(cls.id.desc()).first()
