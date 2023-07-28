from flask import Blueprint, url_for, abort, request, g
from sqlalchemy import select

from . import db
from .models import Poll, PollOption, Comment
from .schemas import PollSchema, NewPollSchema, CommentSchema, VoteSchema
from .auth import auth_required

polls = Blueprint("polls", __name__)

poll_schema = PollSchema()
new_poll_schema = NewPollSchema()
comment_schema = CommentSchema()
vote_schema = VoteSchema()


@polls.post("/polls")
@auth_required
def create_poll():
    """Create a new poll"""

    # Ensure correct data was submitted
    new_poll_data = new_poll_schema.load(request.json)

    # Add new poll to database
    options = new_poll_data.pop("options")
    new_poll = Poll(creator=g.user, **new_poll_data)
    db.session.add(new_poll)
    for option in options:
        new_option = PollOption(poll=new_poll, name=option)
        db.session.add(new_option)
    db.session.commit()

    # Return newly created poll
    return poll_schema.dump(new_poll), 201, {
        "location": url_for("polls.get_poll", id=new_poll.id)
    }


@polls.post("/polls/<int:id>/comments")
@auth_required
def create_comment(id: int):
    """Create a new comment on a specified poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)
    if not poll: 
        abort(404, description="No poll was found for the specified id")

    # Ensure correct data was submitted
    new_comment_data = comment_schema.load(request.json)
    
    # Add new comment to the database
    new_comment = Comment(creator=g.user, poll=poll, **new_comment_data)
    db.session.add(new_comment)
    db.session.commit()

    # Return newly created comment
    return comment_schema.dump(new_comment), 201


@polls.get("/polls")
def get_polls():
    """Get a collection of polls"""

    # Query database for polls
    query = select(Poll)

    # Sort according to query parameter
    sort = request.args.get("sort")
    if sort == "new":
        query = query.order_by(Poll.timestamp.desc())
    elif sort == "top": 
        query = query.order_by(Poll.total_votes.desc())

    # Filter according to query parameter
    tag = request.args.get("tag")
    if tag:
        query = query.where(Poll.tag == tag)

    return poll_schema.dump(db.session.scalars(query).all(), many=True)


@polls.get("/polls/<int:id>")
def get_poll(id: int):
    """Get a poll by its id"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)
    if not poll: 
        abort(404, description="No poll was found for the specified id")
    
    return poll_schema.dump(poll)


@polls.get("/polls/<int:id>/comments")
def get_comments(id: int):
    """Get a collection of comments on a specified poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)
    if not poll: 
        abort(404, description="No poll was found for the specified id")
    
    return comment_schema.dump(poll.comments, many=True)


@polls.patch("/polls/<int:id>/vote")
@auth_required
def vote(id: int):
    """Submit a vote for a poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)
    if not poll: 
        abort(404, description="No poll was found for the specified id")
    
    # Ensure correct data was submitted
    vote_data = vote_schema.load(request.json)
    option = next((option for option in poll.options if option.name == vote_data["vote"]), None)
    if not option: 
        abort(400, description="Invalid vote")
    
    # Ensure voter has not already voted on this poll
    if g.user in poll.voters:
        abort(409, description="User has already voted on this poll")
        
    # Update poll with new vote
    option.votes += 1
    option.voters.append(g.user)
    db.session.commit()

    # Return updated poll
    return poll_schema.dump(poll), {
        "location": url_for("polls.get_poll", id=poll.id)
    }


@polls.delete("/polls/<int:id>")
@auth_required
def delete_poll(id: int): 
    """Delete a poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)
    if not poll: 
        abort(404, description="No poll was found for the specified id")

    # Ensure user has correct permissions
    if g.user.id != poll.creator.id: 
        abort(403)

    # Delete poll
    db.session.delete(poll)
    db.session.commit()

    return "", 204


@polls.delete("/comments/<int:id>")
@auth_required
def delete_comment(id: int):
    """Delete a comment"""

    # Query database for comment
    comment = db.session.get(Comment, id)
    if not comment:
        abort(404, description="No comment was found for the specified id")

    # Ensure user has correct permissions
    if g.user.id != comment.creator.id: 
        abort(403)

    # Delete comment
    db.session.delete(comment)
    db.session.commit()

    return "", 204

    