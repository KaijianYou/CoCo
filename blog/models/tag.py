from .mixin import db, Model


article_tags = \
    db.Table('article_tags',
             db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
             db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True))


class Tag(Model):
    __tablename__ = 'tags'

    name = db.Column(db.String(20), index=True, unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Tag({self.name!r})>'