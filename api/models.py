from sqlalchemy import Table, Column, ForeignKey, String, Text, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from datetime import date, datetime

from . import db

voters_table = Table(
    "voters",
    db.metadata,
    Column("voter_id", ForeignKey("users.id")),
    Column("option_id", ForeignKey("poll_options.id"))
)


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    password: Mapped[str] = mapped_column(String(128))
    date_joined: Mapped[date] = mapped_column(default=datetime.utcnow)

    polls: Mapped[list["Poll"]] = relationship(
        back_populates="creator", 
        cascade="all, delete", 
        order_by="desc(Poll.timestamp)"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="creator", 
        cascade="all, delete", 
        order_by="desc(Comment.timestamp)"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs.get("password"))

    def __repr__(self) -> str:
        return f"<User #{self.id}>"

    def serialize(self) -> dict:
        return {
            "username": self.username,
            "dateJoined": self.date_joined
        }

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class Poll(db.Model):
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(128))
    tag: Mapped[Optional[str]] = mapped_column(String(32))
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    creator: Mapped["User"] = relationship(
        back_populates="polls"
    )

    options: Mapped[list["PollOption"]] = relationship(
        back_populates="poll", 
        cascade="all, delete", 
        order_by="PollOption.id"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="poll", 
        cascade="all, delete",
        order_by="Comment.timestamp"
    )

    def __repr__(self) -> str:
        return f"<Poll #{self.id}>"

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "creator": self.creator.username,
            "title": self.title,
            "options": [option.serialize() for option in self.options],
            "totalVotes": self.total_votes,
            "voters": [voter.username for voter in self.voters],
            "tag": self.tag,
            "timestamp": self.timestamp,
            "numComments": len(self.comments)
        }

    @hybrid_property
    def total_votes(self) -> int:
        return sum(option.votes for option in self.options)

    @total_votes.inplace.expression
    @classmethod
    def total_votes(cls):
        return select(func.sum(PollOption.votes)).where(PollOption.poll_id == cls.id).label("total_votes")

    @property
    def voters(self) -> list[User]:
        return [voter for option in self.options for voter in option.voters]


class PollOption(db.Model):
    __tablename__ = "poll_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    name: Mapped[str] = mapped_column(String(128))
    votes: Mapped[int] = mapped_column(default=0)

    poll: Mapped["Poll"] = relationship(back_populates="options")
    voters: Mapped[list["User"]] = relationship(secondary=voters_table)

    def __repr__(self) -> str:
        return f"<Poll Option #{self.id}>"

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "votes": self.votes,
            "percentage": self.percentage,
            "voters": [voter.username for voter in self.voters]
        }

    @property
    def percentage(self) -> int:
        return round(100 * self.votes / self.poll.total_votes) if self.poll.total_votes != 0 else 0


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    creator: Mapped["User"] = relationship(back_populates="comments")
    poll: Mapped["Poll"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment #{self.id}>"

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "creator": self.creator.username,
            "pollId": self.poll.id,
            "pollTitle": self.poll.title,
            "content": self.content,
            "timestamp": self.timestamp
        }
