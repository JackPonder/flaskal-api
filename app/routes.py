from flask import Blueprint, jsonify, url_for, request
from werkzeug.security import generate_password_hash

from . import db
from .models import User
from .errors import error

routes = Blueprint("routes", __name__)


@routes.route("/users/<int:id>", methods=["GET"])
def get_user(id: int):
    """Get a user by their id from the database"""

    # Query user from database
    user = db.session.get(User, id)

    # Return an error if no user was found
    if not user:
        return error(404, "invalid user id")
    
    return jsonify(user.serialize())


@routes.route("/users", methods=["POST"])
def create_user():
    """Add a new user to the database"""

    # Ensure correct data was submitted
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
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
