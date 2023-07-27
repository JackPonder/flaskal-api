from flask import Blueprint, url_for, abort, request, g
from sqlalchemy import select

from . import db
from .models import User
from .schemas import UserSchema, NewUserSchema, PollSchema, CommentSchema
from .auth import auth_required

users = Blueprint("users", __name__)

user_schema = UserSchema()
new_user_schema = NewUserSchema()
poll_schema = PollSchema()
comment_schema = CommentSchema()


@users.post("/users")
def create_user():
    """Register a new user"""

    # Ensure correct data was submitted
    new_user_data = new_user_schema.load(request.json)

    # Add new user to database
    new_user = User(**new_user_data)
    db.session.add(new_user)
    db.session.commit()
    
    # Return newly created user
    return user_schema.dump(new_user), 201, {
        "location": url_for("users.get_user", username=new_user.username)
    }


@users.get("/users/<string:username>")
def get_user(username: str):
    """Get a user by their username"""

    # Query user from database
    user = db.session.scalars(select(User).where(User.username == username).limit(1)).first()
    if not user: 
        abort(404, description="No user was found for the specified username")
    
    return user_schema.dump(user)


@users.get("/users/self")
@auth_required
def get_authenticated_user():
    return user_schema.dump(g.user)


@users.get("/users/<string:username>/polls")
def get_polls(username: str):
    """Get a collection of all of a user's polls"""

    # Query user from database
    user = db.session.scalars(select(User).where(User.username == username).limit(1)).first()
    if not user: 
        abort(404, description="No user was found for the specified username")
    
    return poll_schema.dump(user.polls, many=True)


@users.get("/users/<string:username>/comments")
def get_comments(username: str):
    """Get a collection of all of a user's comments"""

    # Query user from database
    user = db.session.scalars(select(User).where(User.username == username).limit(1)).first()
    if not user: 
        abort(404, description="No user was found for the specified username")
    
    return comment_schema.dump(user.comments, many=True)


@users.delete("/users/<string:username>")
@auth_required
def delete_user(username: str):
    """Delete a user"""

    # Query user from database
    user = db.session.scalars(select(User).where(User.username == username).limit(1)).first()
    if not user: 
        abort(404, description="No user was found for the specified username")

    # Ensure user has correct permissions
    if g.user.id != user.id: 
        abort(403)

    # Delete user
    db.session.delete(user)
    db.session.commit()

    return "", 204
