from flask import Blueprint, url_for, abort, request, g

from . import db
from .models import User
from .auth import auth_required

users = Blueprint("users", __name__)


@users.post("/users")
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
    return new_user.serialize(), 201, {"location": url_for("users.get", username=new_user.username)}


@users.get("/users/<string:username>")
def get(username: str):
    """Get a user by their id"""

    # Query user from database
    user = db.session.query(User).filter_by(username=username).first()
    if not user: 
        abort(404, description="No user was found for the specified username")
    
    return user.serialize()


@users.get("/users/<string:username>/polls")
def polls(username: str):
    """Get a collection of all of a user's polls"""

    # Query user from database
    user = db.session.query(User).filter_by(username=username).first()
    if not user: 
        abort(404, description="No user was found for the specified username")
    
    return [poll.serialize() for poll in user.polls]


@users.get("/users/<string:username>/comments")
def comments(username: str):
    """Get a collection of all of a user's comments"""

    # Query user from database
    user = db.session.query(User).filter_by(username=username).first()
    if not user: 
        abort(404, description="No user was found for the specified username")
    
    return [comment.serialize() for comment in user.comments]


@users.delete("/users/<string:username>")
@auth_required
def delete(username: str):
    """Delete a user"""

    # Query user from database
    user = db.session.query(User).filter_by(username=username).first()
    if not user: 
        abort(404, description="No user was found for the specified username")

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
