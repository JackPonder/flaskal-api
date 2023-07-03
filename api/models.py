from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
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

    polls: Mapped[List["Poll"]] = relationship(back_populates="creator", cascade="all, delete")
    comments: Mapped[List["Comment"]] = relationship(back_populates="creator", cascade="all, delete")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs.get("password"))

    def __repr__(self) -> str:
        return f"<User #{self.id}>"
    
    def serialize(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "dateJoined": self.date_joined,
        }
    
    def check_password(self, password: str) -> bool: 
        return check_password_hash(self.password, password)


class Poll(db.Model):
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column()
    tag: Mapped[Optional[str]] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.today)
    
    creator: Mapped["User"] = relationship(back_populates="polls")
    options: Mapped[List["PollOption"]] = relationship(back_populates="poll", cascade="all, delete")
    comments: Mapped[List["Comment"]] = relationship(back_populates="poll", cascade="all, delete")

    def __repr__(self) -> str:
        return f"<Poll #{self.id}>"
    
    def serialize(self) -> dict:
        return {
            "id": self.id,
            "creator": self.creator.username,
            "title": self.title,
            "options": [option.serialize() for option in self.options],
            "totalVotes": self.get_total_votes(),
            "voters": [voter.username for voter in self.get_voters()],
            "tag": self.tag,
            "timestamp": self.timestamp
        }
    
    def get_total_votes(self) -> int:
        return sum([option.votes for option in self.options])
    
    def get_voters(self) -> list[User]:
        return [voter for option in self.options for voter in option.voters]


class PollOption(db.Model):
    __tablename__ = "poll_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    name: Mapped[str] = mapped_column()
    votes: Mapped[int] = mapped_column(default=0)

    poll: Mapped["Poll"] = relationship(back_populates="options")
    voters: Mapped[List["User"]] = relationship(secondary=voters_table)

    def __repr__(self) -> str:
        return f"<Poll Option #{self.id}>"
    
    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "votes": self.votes,
            "voters": [voter.username for voter in self.voters]
        }


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)    
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    content: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.today)

    creator: Mapped["User"] = relationship(back_populates="comments")
    poll: Mapped["Poll"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment #{self.id}>"
    
    def serialize(self) -> dict:
        return {
            "creator": self.creator.username,
            "poll": self.poll.title,
            "content": self.content,
            "timestamp": self.timestamp
        }
