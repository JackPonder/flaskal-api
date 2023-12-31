from sqlalchemy import Table, Column, ForeignKey, SQLColumnExpression, String, Text, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
    pass


voters_table = Table(
    "voters",
    Base.metadata,
    Column("voter_id", ForeignKey("users.id"), primary_key=True),
    Column("option_id", ForeignKey("poll_options.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    password: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    polls: Mapped[list["Poll"]] = relationship(
        back_populates="creator", 
        cascade="all, delete", 
        order_by="desc(Poll.created_at)"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="creator", 
        cascade="all, delete", 
        order_by="desc(Comment.created_at)"
    )

    voted_options: Mapped[list["PollOption"]] = relationship(
        secondary=voters_table,
        back_populates="voters"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = pbkdf2_sha256.hash(self.password)

    def __repr__(self) -> str:
        return f"<User #{self.id}>"

    def check_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, self.password)


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(128))
    tag: Mapped[Optional[str]] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    creator: Mapped["User"] = relationship(back_populates="polls")

    options: Mapped[list["PollOption"]] = relationship(
        back_populates="poll", 
        cascade="all, delete", 
        order_by="PollOption.id"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="poll", 
        cascade="all, delete",
        order_by="desc(Comment.created_at)"
    )

    def __repr__(self) -> str:
        return f"<Poll #{self.id}>"

    @hybrid_property
    def total_votes(self) -> int:
        return sum(option.votes for option in self.options)

    @total_votes.inplace.expression
    @classmethod
    def total_votes_expression(cls) -> SQLColumnExpression[int]:
        return select(func.sum(PollOption.votes)).where(PollOption.poll_id == cls.id).label("total_votes")

    @property
    def voters(self) -> list[User]:
        return [voter for option in self.options for voter in option.voters]
    
    @property
    def num_comments(self) -> int:
        return len(self.comments)


class PollOption(Base):
    __tablename__ = "poll_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    name: Mapped[str] = mapped_column(String(128))
    votes: Mapped[int] = mapped_column(default=0)

    poll: Mapped["Poll"] = relationship(back_populates="options")

    voters: Mapped[list["User"]] = relationship(
        secondary=voters_table,
        back_populates="voted_options"
    )

    def __repr__(self) -> str:
        return f"<Poll Option #{self.id}>"

    @property
    def percentage(self) -> int:
        return round(100 * self.votes / self.poll.total_votes) if self.poll.total_votes != 0 else 0


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    creator: Mapped["User"] = relationship(back_populates="comments")
    poll: Mapped["Poll"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment #{self.id}>"
