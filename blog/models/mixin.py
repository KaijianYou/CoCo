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
    enabled = db.Column(db.Boolean, default=True)

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
    def list(cls, enabled=None, order='asc'):
        query = cls.query
        if enabled is not None:
            query = query.filter_by(enabled=enabled)
        order_param = cls.id.asc() if order == 'asc' else cls.id.desc()
        return query.order_by(order_param).all()


class Model(ModelMixin, db.Model):
    __abstract__ = True
