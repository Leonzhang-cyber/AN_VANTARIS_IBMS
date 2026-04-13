# src/imbs/models/hello.py
from src.core.database import db
from datetime import datetime

class Hello(db.Model):
    __tablename__ = 'hello'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    email = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }