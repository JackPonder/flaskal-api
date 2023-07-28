from marshmallow import Schema, ValidationError, fields, validates
from sqlalchemy import select

from . import db
from .models import User


class BaseSchema(Schema):
    def on_bind_field(self, field_name, field_obj):
        name_parts = iter((field_obj.data_key or field_name).split("_"))
        field_obj.data_key = next(name_parts) + "".join(s.title() for s in name_parts)


class UserSchema(BaseSchema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    date_joined = fields.Date(dump_only=True)

    @validates("username")
    def validate_username(self, value):
        if len(value) < 4 or len(value) > 20:
            raise ValidationError("Username must be 4-20 characters")

        if db.session.scalars(select(User).where(User.username == value).limit(1)).first():
            raise ValidationError("Username already in use")
        
    @validates("password")
    def validate_password(self, value):
        if len(value) < 4:
            raise ValidationError("Password must be at least 4 characters")


class NewPollSchema(BaseSchema):
    title = fields.Str(required=True)
    options = fields.List(fields.Str(), required=True)
    tag = fields.Str(allow_none=True)

    @validates("title")
    def validate_title(self, value): 
        if not value: 
            raise ValidationError("Title must not be blank")

    @validates("options")
    def validate_options(self, value):
        if len(value) < 2 or len(value) > 6:
            raise ValidationError("Poll must have 2-6 options")
        
        if any(not option for option in value): 
            raise ValidationError("All options must not be blank")
        
        if len(set(value)) != len(value):
            raise ValidationError("Poll must not have duplicate options")

    @validates("tag")
    def validate_tag(self, value):
        if value is not None and not value: 
            raise ValidationError("Tag must not be blank")


class PollOptionSchema(BaseSchema):
    name = fields.Str()
    votes = fields.Int()
    percentage = fields.Float()
    voters = fields.Pluck(UserSchema, "username", many=True)


class PollSchema(BaseSchema):
    id = fields.Int()
    creator = fields.Pluck(UserSchema, "username")
    title = fields.Str()
    options = fields.Nested(PollOptionSchema, many=True)
    total_votes = fields.Int()
    voters = fields.Pluck(UserSchema, "username", many=True)
    tag = fields.Str()
    timestamp = fields.DateTime()
    num_comments = fields.Int()


class CommentSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    creator = fields.Pluck(UserSchema, "username", dump_only=True)
    poll_id = fields.Int(dump_only=True)
    poll_title = fields.Str(attribute="poll.title", dump_only=True)
    content = fields.Str(required=True)
    timestamp = fields.DateTime(dump_only=True)

    @validates("content")
    def validate_content(self, value):
        if not value: 
            raise ValidationError("Content must not be blank")


class VoteSchema(BaseSchema):
    vote = fields.Str(required=True)
