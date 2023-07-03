from flask import abort, request, current_app
from functools import wraps
import jwt

from . import db
from .models import User


def token_required(f): 
    """Decorate a route to require token authentication"""

    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get("authorization")
        if not token:
            abort(401)
        token = token.split(" ")[1]

        try:
            data = jwt.decode(token, current_app.config.get("SECRET_KEY"), algorithms=["HS256"])
            if type(data) != dict: 
                abort(401)

            curent_user = db.session.get(User, data.get("user_id"))
            if not curent_user:
                abort(401)

            return f(curent_user, *args, **kwargs)
        except jwt.PyJWKError:
            abort(401)

    return decorator
