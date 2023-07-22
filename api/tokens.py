from flask import Blueprint, abort, request, current_app
import jwt

from . import db
from .models import User

tokens = Blueprint("tokens", __name__)


@tokens.post("/tokens")
def new_token():
    """Generate a new JWT token for a user"""

    # Get authorization data
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        abort(401)

    # Check user credentials
    current_user = db.session.query(User).filter_by(username=auth.username).first()
    if not current_user or not current_user.check_password(auth.password):
        abort(401)

    # Return JWT token
    token = jwt.encode({"id": current_user.id}, current_app.config.get("SECRET_KEY"))
    return {"token": token}
