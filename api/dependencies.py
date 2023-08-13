from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db.session import SessionLocal
from .db.models import User

basic_auth = HTTPBasic()


def get_db():
    with SessionLocal() as session:
        yield session


def get_auth_user(
    auth: HTTPBasicCredentials = Depends(basic_auth),
    db: Session = Depends(get_db),
):
    """Get the current authenticated user"""

    user = db.scalar(select(User).where(User.username == auth.username))
    if user is None or not user.check_password(auth.password):
        raise HTTPException(401)
    
    return user
