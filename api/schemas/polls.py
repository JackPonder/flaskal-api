from pydantic import Field, AliasPath, field_validator, field_serializer
from datetime import datetime
from typing import Optional

from .base import CamelCaseSchema
from .validators import NonEmptyString
from .users import UserSchema


class NewPollSchema(CamelCaseSchema):
    title: NonEmptyString = Field(max_length=128)
    options: list[NonEmptyString] = Field(min_length=2, max_length=6)
    tag: Optional[NonEmptyString] = Field(max_length=32)

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("Poll must not have duplicate options")

        return value


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
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
    title: str
    options: list[PollOptionSchema]
    total_votes: int
    voters: list[UserSchema]
    tag: Optional[str]
    num_comments: int
    timestamp: datetime

    @field_serializer("voters")
    def serialize_voters(self, voters: list[UserSchema]) -> list[str]: 
        return [voter.username for voter in voters]


class VoteSchema(CamelCaseSchema):
    vote: str
