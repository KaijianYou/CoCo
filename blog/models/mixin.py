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

    @classmethod
    def create(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        return instance.save()

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save() or self

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        return db.session.commit()


class Model(ModelMixin, db.Model):
    __abstract__ = True
