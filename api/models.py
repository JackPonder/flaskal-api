from datetime import date, datetime

from . import db

voters_table = db.Table(
    "voters",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("option_id", db.Integer, db.ForeignKey("poll_options.id")),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    date_joined = db.Column(db.Date, nullable=False, default=date.today())
    polls = db.relationship("Poll", backref="creator")

    def __repr__(self):
        return f"User #{self.id}"
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "dateJoined": self.date_joined,
        }


class Poll(db.Model):
    __tablename__ = "polls"

    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.Text, nullable=False)
    options = db.relationship("PollOption", backref="poll")
    tag = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.today())

    def __repr__(self):
        return f"Poll #{self.id}"
    
    def serialize(self):
        return {
            "id": self.id,
            "creatorId": self.creator_id,
            "title": self.title,
            "options": [option.serialize() for option in self.options],
            "totalVotes": self.get_total_votes(),
            "voters": self.get_all_voters(),
            "tag": self.tag,
            "timestamp": self.timestamp
        }
    
    def get_total_votes(self):
        return sum([option.votes for option in self.options])
    
    def get_all_voters(self):
        return [voter.id for option in self.options for voter in option.voters]


class PollOption(db.Model):
    __tablename__ = "poll_options"

    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("polls.id"), nullable=False)
    name = db.Column(db.Text, nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)
    voters = db.relationship("User", secondary=voters_table, backref="voted_options")

    def __repr__(self):
        return f"Poll Option #{self.id}"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "votes": self.votes,
            "voters": [voter.id for voter in self.voters]
        }
