from datetime import datetime

from sqlalchemy.orm.interfaces import MapperExtension

from blog.extensions import db
from blog.search import query_index, add_to_index, remove_from_index


class ModelUpdateExtension(MapperExtension):
    def before_update(self, mapper, connection, instance):
        if hasattr(instance, 'utc_updated'):
            instance.utc_updated = datetime.utcnow()


class ModelMixin:
    __mapper_args__ = {
        'extension': ModelUpdateExtension()
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    utc_created = db.Column(db.DateTime(False), default=datetime.utcnow)
    utc_updated = db.Column(db.DateTime(False), default=datetime.utcnow)
    enabled = db.Column(db.Boolean, default=True)  # 表示是否逻辑删除

    @classmethod
    def create(cls, *args, **kwargs):
        try:
            instance = cls(*args, **kwargs)
            instance.save()
        except Exception as e:
            db.session.rollback()
            raise e
        else:
            return instance

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)  # setattr 可以触发 property 属性的更新操作
        return self.save() or self

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        return db.session.commit()

    @classmethod
    def get_by_id(cls, id, enabled=None):
        query = cls.query
        if enabled is not None:
            query = query.filter_by(enabled=enabled)
        return query.filter_by(id=id).first()

    @classmethod
    def list_all(cls, enabled=None, order='asc'):
        query = cls.query
        if enabled is not None:
            query = query.filter_by(enabled=enabled)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).all()


class SearchableMixin:
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).filter_by(enabled=True)\
            .order_by(db.case(when, value=cls.id)).all(), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': [obj for obj in session.new if isinstance(obj, cls)],
            'update': [obj for obj in session.dirty if isinstance(obj, cls)],
            'delete': [obj for obj in session.deleted if isinstance(obj, cls)]
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['delete']:
            remove_from_index(cls.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class Model(ModelMixin, db.Model):
    __abstract__ = True
