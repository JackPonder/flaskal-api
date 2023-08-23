from pydantic import Field, AliasPath
from datetime import datetime

from .base import CamelCaseSchema
from .validators import NonEmptyString


class NewCommentSchema(CamelCaseSchema):
    content: NonEmptyString


class CommentSchema(CamelCaseSchema):
    id: int
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
    poll_id: int
    poll_title: str = Field(validation_alias=AliasPath("poll", "title"), serialization_alias="pollTitle")
    content: str
    created_at: datetime
