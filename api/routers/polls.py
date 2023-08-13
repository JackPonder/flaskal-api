from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..dependencies import get_db, get_auth_user
from ..db.models import User, Poll, PollOption
from ..schemas.polls import NewPollSchema, PollSchema

router = APIRouter()


@router.post("/polls", response_model=PollSchema, status_code=201)
def create_poll(
    poll_data: NewPollSchema, 
    db: Session = Depends(get_db),
    user: User = Depends(get_auth_user),
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


@router.get("/polls", response_model=list[PollSchema])
def get_polls(
    sort: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db)
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
