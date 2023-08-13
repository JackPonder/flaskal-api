from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..dependencies import get_db, get_auth_user
from ..db.models import User, Poll, PollOption, Comment
from ..schemas.polls import NewPollSchema, PollSchema
from ..schemas.comments import NewCommentSchema, CommentSchema

router = APIRouter()


@router.post("/polls", response_model=PollSchema, status_code=201)
def create_poll(
    poll_data: NewPollSchema, 
    user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
):
    """Create a poll"""

    # Add new poll to the database
    data = poll_data.model_dump()
    options: list[str] = data.pop("options")
    new_poll = Poll(creator=user, **data)
    db.add(new_poll)
    for option in options:
        new_option = PollOption(poll=new_poll, name=option)
        db.add(new_option)
    db.commit()

    return new_poll


@router.post("/polls/{poll_id}/comments", response_model=CommentSchema, status_code=201)
def create_comment(
    poll_id: int,
    comment_data: NewCommentSchema,
    user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),    
):
    """Create a comment on a poll"""

    # Ensure poll exists
    poll = db.get(Poll, poll_id)
    if poll is None:
        raise HTTPException(404, "No poll was found for the specified id")

    # Add comment to the database
    new_comment = Comment(poll=poll, creator=user, **comment_data.model_dump())
    db.add(new_comment)
    db.commit()

    return new_comment


@router.get("/polls", response_model=list[PollSchema])
def get_polls(
    sort: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db),
): 
    """Get a collection of polls"""

    # Query database for polls
    query = select(Poll)

    # Sort polls
    if sort == "new":
        query = query.order_by(Poll.timestamp.desc())
    elif sort == "top":
        query = query.order_by(Poll.total_votes.desc())

    # Filter polls
    if tag is not None:
        query = query.where(Poll.tag == tag)

    return db.scalars(query).all()


@router.get("/polls/{poll_id}", response_model=PollSchema)
def get_poll(
    poll_id: int,
    db: Session = Depends(get_db),
):
    """Get a poll by its id"""

    # Get poll if it exists
    poll = db.get(Poll, poll_id)
    if poll is None:
        raise HTTPException(404, "No poll was found for the specified id")
    
    return poll


@router.get("/polls/{poll_id}/comments", response_model=list[CommentSchema])
def get_comments(
    poll_id: int,
    db: Session = Depends(get_db),    
):
    """Get a collection of a poll's comments"""

    # Get poll if it exists
    poll = db.get(Poll, poll_id)
    if poll is None:
        raise HTTPException(404, "No poll was found for the specified id")
    
    return poll.comments


@router.delete("/polls/{poll_id}", status_code=204)
def delete_poll(
    poll_id: int,
    user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
):
    """Delete a poll"""

    # Get poll if its exists
    poll = db.get(Poll, poll_id)
    if poll is None:
        raise HTTPException(404, "No poll was found for the specified id")
    
    # Ensure user is authorized to delete this poll
    if user.id != poll.creator_id:
        raise HTTPException(403)
    
    # Delete poll from the database
    db.delete(poll)
    db.commit()