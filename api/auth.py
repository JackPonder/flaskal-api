from flask import abort, request, g
from functools import wraps

from . import db
from .models import User


def auth_required(f): 
    """Decorate a route to require an authenticated user"""

    @wraps(f)
    def decorator(*args, **kwargs):
        auth = request.authorization
        if not auth:
            abort(401)

        user = db.session.query(User).filter_by(username=auth.username).first()
        if not user or not user.check_password(auth.password):
            abort(401)
        g.user = user

        return f(*args, **kwargs)

    return decorator
