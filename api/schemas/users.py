from datetime import date

from .base import CamelCaseSchema


class NewUserSchema(CamelCaseSchema):
    username: str
    password: str


class UserSchema(CamelCaseSchema):
    username: str
    date_joined: date
