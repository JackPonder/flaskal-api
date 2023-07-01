from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import date, datetime

from . import db

voters_table = Table(
    "voters",
    db.metadata,
    Column("voter_id", ForeignKey("users.id")),
    Column("option_id", ForeignKey("poll_options.id")),
)


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    date_joined: Mapped[date] = mapped_column(default=date.today)
    polls: Mapped[List["Poll"]] = relationship(backref="creator")
    comments: Mapped[List["Comment"]] = relationship(backref="creator")

    def __repr__(self) -> str:
        return f"<User #{self.id}>"
    
    def serialize(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "dateJoined": self.date_joined,
        }


class Poll(db.Model):
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column()
    options: Mapped[List["PollOption"]] = relationship(backref="poll")
    tag: Mapped[Optional[str]] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.today)
    comments: Mapped[List["Comment"]] = relationship(backref="poll")

    def __repr__(self) -> str:
        return f"<Poll #{self.id}>"
    
    def serialize(self) -> dict:
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
    
    def get_total_votes(self) -> int:
        return sum([option.votes for option in self.options])
    
    def get_all_voters(self) -> list:
        return [voter.id for option in self.options for voter in option.voters]


class PollOption(db.Model):
    __tablename__ = "poll_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    name: Mapped[str] = mapped_column()
    votes: Mapped[int] = mapped_column(default=0)
    voters: Mapped[List["User"]] = relationship(secondary=voters_table)

    def __repr__(self) -> str:
        return f"<Poll Option #{self.id}>"
    
    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "votes": self.votes,
            "voters": [voter.id for voter in self.voters]
        }


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)    
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    content: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.today)

    def __repr__(self) -> str:
        return f"<Comment #{self.id}>"
    
    def serialize(self) -> dict:
        return {
            "id": self.id,
            "creatorId": self.creator_id,
            "content": self.content,
            "timestamp": self.timestamp
        }
