from flask import Blueprint, abort, request, current_app
import jwt

from . import db
from .models import User

tokens= Blueprint("tokens", __name__)


@tokens.route("/tokens", methods=["POST"])
def create():
    """Generate a new JWT token for a user"""

    # Ensure correct data was submitted
    data = request.authorization
    if not data: 
        abort(400)

    # Check user credentials
    user = db.session.query(User).filter_by(username=data.username).first()
    if not user or not user.check_password(data.password): 
        abort(401)

    # Return JWT token for the user
    token = jwt.encode({"user_id": user.id}, current_app.config.get("SECRET_KEY"), algorithm="HS256")
    return {"token": token}
