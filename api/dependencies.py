from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import os
import jwt

from .db.session import SessionLocal
from .db.models import User

bearer_auth = HTTPBearer()


def get_db():
    with SessionLocal() as session:
        yield session


def get_auth_user(
    auth: HTTPAuthorizationCredentials = Depends(bearer_auth),
    db: Session = Depends(get_db),
):
    """Get the current authenticated user"""

    try:
        payload = jwt.decode(auth.credentials, os.environ.get("SECRET_KEY"), ["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401)

    if not isinstance(payload, dict):
        raise HTTPException(401)

    user = db.get(User, payload.get("sub"))
    if user is None:
        raise HTTPException(401)

    return user
