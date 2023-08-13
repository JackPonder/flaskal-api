from pydantic import Field, AliasPath
from datetime import datetime

from .base import CamelCaseSchema


class NewPollSchema(CamelCaseSchema):
    title: str
    options: list[str]
    tag: str | None


class PollOptionSchema(CamelCaseSchema):
    name: str
    votes: int
    voters: list[str]
    percentage: float


class PollSchema(CamelCaseSchema):
    id: int
    creator: str = Field(alias=AliasPath("creator", "username"))
    title: str
    options: list[PollOptionSchema]
    total_votes: int
    voters: list[str]
    tag: str | None
    num_comments: int
    timestamp: datetime
