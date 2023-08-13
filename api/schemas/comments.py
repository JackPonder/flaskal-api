from pydantic import Field, AliasPath
from datetime import datetime

from .base import CamelCaseSchema


class NewCommentSchema(CamelCaseSchema):
    content: str


class CommentSchema(CamelCaseSchema):
    id: int
    creator: str = Field(alias=AliasPath("creator", "username"))
    poll_id: int = Field(alias=AliasPath("poll", "id"))
    poll_title: str = Field(alias=AliasPath("poll", "title"))
    content: str
    timestamp: datetime