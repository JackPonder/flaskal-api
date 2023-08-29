from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..dependencies import DatabaseSession, AuthenticatedUser
from ..db.models import User
from ..schemas.users import NewUserSchema, UserSchema
from ..schemas.polls import PollSchema
from ..schemas.comments import CommentSchema

router = APIRouter(tags=["Users"])


@router.post("/users", response_model=UserSchema, status_code=201)
def create_user(
    user_data: NewUserSchema, 
    db: DatabaseSession,
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


@router.get("/users/self", response_model=UserSchema)
def get_self(
    user: AuthenticatedUser
):
    """Get a user via their JWT access token"""

    return user


@router.get("/users/{username}", response_model=UserSchema)
def get_user(
    username: str, 
    db: DatabaseSession,
):
    """Get a user by their username"""

    # Get user if they exist
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(404, "No user was found for the specified username")

    return user


@router.get("/users/{username}/polls", response_model=list[PollSchema])
def get_polls(
    username: str, 
    db: DatabaseSession,
):
    """Get a collection of a user's polls"""

    # Get user if they exist
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(404, "No user was found for the specified username")

    return user.polls


@router.get("/users/{username}/comments", response_model=list[CommentSchema])
def get_comments(
    username: str, 
    db: DatabaseSession,
):
    """Get a collection of a user's comments"""

    # Get user if they exist
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(404, "No user was found for the specified username")

    return user.comments


@router.delete("/users/{username}", status_code=204)
def delete_user(
    username: str, 
    user: AuthenticatedUser,
    db: DatabaseSession,
):
    """Delete a user"""

    # Get user if they exist
    deleted_user = db.scalar(select(User).where(User.username == username))
    if deleted_user is None:
        raise HTTPException(404, "No user was found for the specified username")
    
    # Ensure user is authorized to delete this user
    if user.id != deleted_user.id:
        raise HTTPException(403)

    # Delete user from the database
    db.delete(deleted_user)
    db.commit()
