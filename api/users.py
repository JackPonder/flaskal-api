from flask import Blueprint, jsonify, url_for, request
from werkzeug.security import generate_password_hash

from . import db
from .models import User
from .errors import error_response

users = Blueprint("users", __name__)


@users.route("/users", methods=["POST"])
def create():
    """Register a new user"""

    # Ensure correct data was submitted
    json = request.get_json() or {}
    username = json.get("username")
    password = json.get("password")
    if not username or not password:
        return error_response(message="invalid data")
    
    # Ensure username is not already in use
    if db.session.query(User).filter_by(username=username).first():
        return error_response(message="username already in use")
        
    # Add new user to database
    new_user = User(username=username, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    # Return newly created user
    response = jsonify(new_user.serialize())
    response.status_code = 201
    response.headers["Location"] = url_for("users.get", id=new_user.id)
    return response


@users.route("/users/<int:id>", methods=["GET"])
def get(id: int):
    """Get a user by their id"""

    # Query user from database
    user = db.session.get(User, id)

    # Return an error if no user was found
    if not user:
        return error_response(404, "invalid user id")
    
    return jsonify(user.serialize())
