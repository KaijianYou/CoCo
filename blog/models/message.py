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

    def to_json(self):
        return {
            'id': self.id,
            'received_time': (self.utc_created + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
            'body': self.body
        }
