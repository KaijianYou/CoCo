from .mixin import db


article_tag = \
    db.Table('article_tag',
             db.Column('tag_id',
                       db.Integer,
                       db.ForeignKey('tags.id'), primary_key=True),
             db.Column('article_id',
                       db.Integer,
                       db.ForeignKey('articles.id'), primary_key=True))

