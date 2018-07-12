from datetime import datetime

from sqlalchemy.orm.interfaces import MapperExtension

from blog.extensions import db


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
    is_enable = db.Column(db.Boolean, default=True)

    @classmethod
    def create(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        return instance.save()

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
    def query_by_id(cls, id, is_enable=None):
        query = cls.query
        if is_enable is not None:
            query = query.filter_by(is_enable=is_enable)
        return query.filter_by(id=id).first()

    @classmethod
    def query_all(cls, is_enable=None, order='asc'):
        query = cls.query
        if is_enable is not None:
            query = query.filter_by(is_enable=is_enable)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).all()


class Model(ModelMixin, db.Model):
    __abstract__ = True
