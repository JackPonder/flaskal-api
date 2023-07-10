from flask import abort, request, g, current_app
from functools import wraps
import jwt

from . import db
from .models import User


def auth_required(f): 
    """Decorate a route to require an authenticated user"""

    @wraps(f)
    def decorator(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or len(auth.split()) < 2:
            abort(401)
        token = auth.split()[1]

        try:
            data = jwt.decode(token, current_app.config.get("SECRET_KEY"), algorithms=["HS256"])
        except jwt.PyJWTError:
            abort(401)
        
        user = db.session.get(User, data.get("id"))
        if not user:
            abort(401)
        g.user = user

        return f(*args, **kwargs)

    return decorator
