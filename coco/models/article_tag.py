from .mixin import db, Model


class ArticleTag(Model):
    __tablename__ = 'article_tag'
    __table_args__ = (
        db.UniqueConstraint('article_id', 'tag_id'),
    )

    article_id = db.Column(db.Integer, nullable=False, comment='外键，文章的ID')
    tag_id = db.Column(db.Integer, nullable=False, comment='外键，标签的ID')