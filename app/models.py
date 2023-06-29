from datetime import date

from . import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    date_joined = db.Column(db.Date, nullable=False, default=date.today())

    def __repr__(self):
        return f"User #{self.id}"
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "dateJoined": self.date_joined,
        }
