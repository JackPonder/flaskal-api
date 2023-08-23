from pydantic import Field
from datetime import datetime

from .base import CamelCaseSchema


class NewUserSchema(CamelCaseSchema):
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=4)


class UserSchema(CamelCaseSchema):
    username: str
    created_at: datetime
