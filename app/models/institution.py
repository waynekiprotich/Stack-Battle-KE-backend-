from extensions import db
from datetime import datetime

class Institution(db.Model):
    __tablename__ = 'institutions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # (One-to-Many) One institution has many users
    users = db.relationship('User', backref='institution', lazy='dynamic')