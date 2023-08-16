from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

import os
import jwt

from ..dependencies import get_db
from ..db.models import User
from ..schemas.tokens import AccessTokenSchema

router = APIRouter(tags=["Tokens"])

basic_auth = HTTPBasic()


@router.post("/tokens", response_model=AccessTokenSchema)
def new_token(
    auth: HTTPBasicCredentials = Depends(basic_auth),
    db: Session = Depends(get_db),
):
    """Get a new JWT access token for a user"""

    user = db.scalar(select(User).where(User.username == auth.username))
    if user is None or not user.check_password(auth.password):
        raise HTTPException(401)
    
    payload = {"sub": user.id}
    access_token = jwt.encode(payload, os.environ.get("SECRET_KEY"), "HS256")

    return {"accessToken": access_token}
