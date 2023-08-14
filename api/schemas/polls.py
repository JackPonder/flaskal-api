from pydantic import Field, AliasPath, field_serializer
from datetime import datetime

from .base import CamelCaseSchema
from .users import UserSchema


class NewPollSchema(CamelCaseSchema):
    title: str
    options: list[str]
    tag: str | None


class PollOptionSchema(CamelCaseSchema):
    name: str
    votes: int
    voters: list[UserSchema]
    percentage: float

    @field_serializer("voters")
    def serialize_voters(self, voters: list[UserSchema]) -> list[str]: 
        return [voter.username for voter in voters]


class PollSchema(CamelCaseSchema):
    id: int
    creator: str = Field(alias=AliasPath("creator", "username"))
    title: str
    options: list[PollOptionSchema]
    total_votes: int
    voters: list[UserSchema]
    tag: str | None
    num_comments: int
    timestamp: datetime

    @field_serializer("voters")
    def serialize_voters(self, voters: list[UserSchema]) -> list[str]: 
        return [voter.username for voter in voters]


class VoteSchema(CamelCaseSchema):
    vote: str
