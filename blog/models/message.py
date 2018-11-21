from datetime import timedelta

from .mixin import db, Model


class Message(Model):
    __tablename__ = 'message'

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.String(200))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Message({self.body!r})>'

    def to_dict(self):
        return {
            'id': self.id,
            'received_time': (self.utc_created + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
            'body': self.body
        }

    @classmethod
    def get_latest_by_sender_id(cls, sender_id, enabled=None):
        query = cls.query
        if enabled is not None:
            query = query.filter_by(enabled=enabled)
        return query.filter_by(sender_id=sender_id).order_by(cls.id.desc()).first()
