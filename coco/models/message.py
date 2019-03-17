from datetime import timedelta

from .mixin import db, Model


class Message(Model):
    __tablename__ = 'message'
    __table_args = (
        db.Index('sender_id', 'recipient_id'),
    )

    sender_id = db.Column(db.Integer(), nullable=False, comment='外键，发送消息的用户ID')
    recipient_id = db.Column(db.Integer(), nullable=False, comment='外键，接收消息的用户ID')
    body = db.Column(db.String(200), nullable=False, comment='内容')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Message({self.body!r})>'

    def to_dict(self):
        return {
            'id': self.id,
            'received_time': (self.created_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
            'body': self.body
        }

    @classmethod
    def get_latest_by_sender_id(cls, sender_id, deleted=None):
        query = cls.query
        if deleted is not None:
            query = query.filter_by(deleted=deleted)
        return query.filter_by(sender_id=sender_id).order_by(cls.id.desc()).first()
