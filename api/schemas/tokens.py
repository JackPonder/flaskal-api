from .base import CamelCaseSchema


class AccessTokenSchema(CamelCaseSchema):
    access_token: str
    token_type: str = "Bearer"
