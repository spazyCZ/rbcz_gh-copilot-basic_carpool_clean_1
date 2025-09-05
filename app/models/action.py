from datetime import datetime
from app.extensions import db


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_username = db.Column(db.String, db.ForeignKey('user.username'))

    user = db.relationship('User')
