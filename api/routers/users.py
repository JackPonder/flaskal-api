from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..db.models import User
from ..schemas.users import NewUserSchema, UserSchema

router = APIRouter()


@router.post("/users", response_model=UserSchema, status_code=201)
def create_user(
    user_data: NewUserSchema, 
    db: Session = Depends(get_db)
):
    """Register a new user"""

    # Ensure username is not taken
    if db.scalar(select(User).where(User.username == user_data.username)):
        raise HTTPException(409, "Username already in use")
    
    # Add user to the database
    new_user = User(**user_data.model_dump())
    db.add(new_user)
    db.commit()

    return new_user


@router.get("/users/{username}", response_model=UserSchema)
def get_user(
    username: str, 
    db: Session = Depends(get_db)
):
    """Get a user by their username"""

    # Get user if they exist
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(404, "No user was found for the specified username")

    return user
