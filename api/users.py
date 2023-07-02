from flask import Blueprint, url_for, abort, request
from werkzeug.security import generate_password_hash

from . import db
from .models import User

users = Blueprint("users", __name__)


@users.route("/users", methods=["POST"])
def create():
    """Register a new user"""

    # Ensure correct data was submitted
    json = request.get_json()
    if type(json) != dict: 
        abort(400, description="Invalid data")
    username = json.get("username")
    password = json.get("password")
    if not username or not password:
        abort(400, description="Invalid data")
    
    # Ensure username is not already in use
    if db.session.query(User).filter_by(username=username).first():
        abort(400, description="Username already in use")
        
    # Add new user to database
    new_user = User(username=username, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    # Return newly created user
    return new_user.serialize(), 201, {"location": url_for("users.get", id=new_user.id)}


@users.route("/users/<int:id>", methods=["GET"])
def get(id: int):
    """Get a user by their id"""

    # Query user from database
    user = db.session.get(User, id) or abort(404, description="No user was found for the specified id")
    
    return user.serialize()


@users.route("/users/<int:id>/polls", methods=["GET"])
def polls(id: int):
    """Get a collection of all of a user's polls"""

    # Query user from database
    user = db.session.get(User, id) or abort(404, description="No user was found for the specified id")
    
    return [poll.serialize() for poll in user.polls]


@users.route("/users/<int:id>/comments", methods=["GET"])
def comments(id: int):
    """Get a collection of all of a user's comments"""

    # Query user from database
    user = db.session.get(User, id) or abort(404, description="No user was found for the specified id")
    
    return [comment.serialize() for comment in user.comments]


@users.route("/users/<int:id>", methods=["DELETE"])
def delete(id: int):
    """Delete a user"""

    # Query user from database
    user = db.session.get(User, id) or abort(404, description="No user was found for the specified id")

    # Delete all of the user's polls and comments
    for comment in user.comments:
        db.session.delete(comment)
    for poll in user.polls:
        for option in poll.options:
            db.session.delete(option)
        db.session.delete(poll)

    # Delete user
    db.session.delete(user)
    db.session.commit()

    return "", 204
