from flask import Blueprint, jsonify, url_for, request
from werkzeug.security import generate_password_hash

from . import db
from .models import User, Poll, PollOption
from .errors import error

routes = Blueprint("routes", __name__)


@routes.route("/users/<int:id>", methods=["GET"])
def get_user(id: int):
    """Get a user by their id"""

    # Query user from database
    user = db.session.get(User, id)

    # Return an error if no user was found
    if not user:
        return error(404, "invalid user id")
    
    return jsonify(user.serialize())


@routes.route("/users", methods=["POST"])
def create_user():
    """Create a new user"""

    # Ensure correct data was submitted
    json = request.get_json() or {}
    username = json.get("username")
    password = json.get("password")
    if not username or not password:
        return error(message="invalid data")
    
    # Ensure username is not already in use
    if db.session.query(User).filter_by(username=username).first():
        return error(message="username already in use")
        
    # Add new user to database
    new_user = User(username=username, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    # Return newly created user
    response = jsonify(new_user.serialize())
    response.status_code = 201
    response.headers["Location"] = url_for("routes.get_user", id=new_user.id)
    return response


@routes.route("/polls/<int:id>", methods=["GET"])
def get_poll(id: int):
    """Get a poll by its id"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)

    # Return an error if no user was found
    if not poll:
        return error(404, "invalid poll id")
    
    return jsonify(poll.serialize())


@routes.route("/polls", methods=["POST"])
def create_poll():
    """Create a new poll"""

    # Ensure correct data was submitted
    json = request.get_json() or {}
    creator = db.session.get(User, json.get("creatorId"))
    title = json.get("title")
    options = json.get("options")
    tag = json.get("tag")
    if not creator or not title or type(options) != list or len(options) < 2:
        return error(message="invalid form data")

    # Add new poll to database
    new_poll = Poll(creator=creator, title=title)
    if tag:
        new_poll.tag = tag
    db.session.add(new_poll)
    for option in options:
        if not option:
            continue
        new_option = PollOption(poll=new_poll, name=option)
        db.session.add(new_option)
    db.session.commit()

    # Return newly created poll
    response = jsonify(new_poll.serialize())
    response.status_code = 201
    response.headers["Location"] = url_for("routes.get_poll", id=new_poll.id)
    return response
