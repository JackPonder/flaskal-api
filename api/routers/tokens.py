from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from typing import Annotated

import os
import jwt

from ..dependencies import DatabaseSession
from ..db.models import User
from ..schemas.tokens import AccessTokenSchema

router = APIRouter(tags=["Tokens"])

basic_auth = HTTPBasic()
BasicAuth = Annotated[HTTPBasicCredentials, Depends(basic_auth)]


@router.post("/tokens", response_model=AccessTokenSchema)
def new_token(
    auth: BasicAuth,
    db: DatabaseSession,
):
    """Get a new JWT access token for a user"""

    user = db.scalar(select(User).where(User.username == auth.username))
    if user is None or not user.check_password(auth.password):
        raise HTTPException(401)
    
    payload = {"sub": user.id}
    access_token = jwt.encode(payload, os.environ.get("SECRET_KEY"), "HS256")

    return {"accessToken": access_token}
