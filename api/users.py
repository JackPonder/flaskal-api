from flask import Blueprint, url_for, abort, request, g

from . import db
from .models import User
from .auth import auth_required

users = Blueprint("users", __name__)


@users.route("/users", methods=["POST"])
def register():
    """Register a new user"""

    # Ensure correct data was submitted
    json = request.get_json()
    if type(json) != dict: 
        abort(400)
    username = json.get("username")
    password = json.get("password")
    if not username or not password:
        abort(400)
    
    # Ensure username is not already in use
    if db.session.query(User).filter_by(username=username).first():
        abort(409, description="Username already in use")
        
    # Add new user to database
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    # Return newly created user
    return new_user.serialize(), 201, {"location": url_for("users.get", id=new_user.id)}


@users.route("/users/<int:id>", methods=["GET"])
def get(id: int):
    """Get a user by their id"""

    # Query user from database
    user = db.session.get(User, id)
    if not user: 
        abort(404, description="No user was found for the specified id")
    
    return user.serialize()


@users.route("/users/<int:id>/polls", methods=["GET"])
def polls(id: int):
    """Get a collection of all of a user's polls"""

    # Query user from database
    user = db.session.get(User, id)
    if not user: 
        abort(404, description="No user was found for the specified id")
    
    return [poll.serialize() for poll in user.polls]


@users.route("/users/<int:id>/comments", methods=["GET"])
def comments(id: int):
    """Get a collection of all of a user's comments"""

    # Query user from database
    user = db.session.get(User, id)
    if not user: 
        abort(404, description="No user was found for the specified id")
    
    return [comment.serialize() for comment in user.comments]


@users.route("/users/<int:id>", methods=["DELETE"])
@auth_required
def delete(id: int):
    """Delete a user"""

    # Query user from database
    user = db.session.get(User, id)
    if not user: 
        abort(404, description="No user was found for the specified id")

    # Ensure user has correct permissions
    if g.user.id != user.id: 
        abort(403)

    # Delete user
    db.session.delete(user)
    db.session.commit()

    return "", 204


@users.get("/users/self")
@auth_required
def get_token_user(): 
    return g.user.serialize()
