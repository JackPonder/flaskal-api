from flask import Blueprint, url_for, abort, request, g

from . import db
from .models import Poll, PollOption, Comment
from .auth import auth_required

polls = Blueprint("polls", __name__)


@polls.post("/polls")
@auth_required
def create_poll():
    """Create a new poll"""

    # Ensure correct data was submitted
    json = request.get_json()
    if type(json) != dict: 
        abort(400)
    title = json.get("title")
    options = json.get("options")
    tag = json.get("tag")
    if not title or type(options) != list or len(options) < 2:
        abort(400)

    # Add new poll to database
    new_poll = Poll(creator=g.user, title=title, tag=tag if tag else None)
    db.session.add(new_poll)
    for option in options:
        new_option = PollOption(poll=new_poll, name=option)
        db.session.add(new_option)
    db.session.commit()

    # Return newly created poll
    return new_poll.serialize(), 201, {"location": url_for("polls.get_poll", id=new_poll.id)}


@polls.post("/polls/<int:id>/comments")
@auth_required
def create_comment(id: int):
    """Create a new comment on a specified poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)
    if not poll: 
        abort(404, description="No poll was found for the specified id")

    # Ensure correct data was submitted
    json = request.get_json()
    if type(json) != dict: 
        abort(400)
    content = json.get("content")
    if not content:
        abort(400)
    
    # Add new comment to the database
    new_comment = Comment(creator=g.user, poll=poll, content=content)
    db.session.add(new_comment)
    db.session.commit()

    # Return newly created comment
    return new_comment.serialize(), 201


@polls.get("/polls")
def get_polls():
    """Get a collection of polls"""

    # Query database for polls
    polls = db.session.query(Poll)

    # Sort according to query parameter
    sort = request.args.get("sort")
    if sort == "new":
        polls = polls.order_by(Poll.timestamp.desc())
    elif sort == "top": 
        polls = polls.order_by(Poll.total_votes.desc())

    # Filter according to query parameter
    tag = request.args.get("tag")
    if tag:
        polls = polls.filter_by(tag=tag)

    return [poll.serialize() for poll in polls.all()]


@polls.get("/polls/<int:id>")
def get_poll(id: int):
    """Get a poll by its id"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)
    if not poll: 
        abort(404, description="No poll was found for the specified id")
    
    return poll.serialize()


@polls.get("/polls/<int:id>/comments")
def get_comments(id: int):
    """Get a collection of comments on a specified poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)
    if not poll: 
        abort(404, description="No poll was found for the specified id")
    
    return [comment.serialize() for comment in poll.comments]


@polls.patch("/polls/<int:id>/vote")
@auth_required
def vote(id: int):
    """Submit a vote for a poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)
    if not poll: 
        abort(404, description="No poll was found for the specified id")
    
    # Ensure correct data was submitted
    json = request.get_json()
    if type(json) != dict: 
        abort(400)
    option = db.session.get(PollOption, json.get("vote"))
    if not option or option not in poll.options:
        abort(400)
    
    # Ensure voter has not already voted on this poll
    if g.user in poll.voters:
        abort(409, description="User has already voted on this poll")
        
    # Update poll with new vote
    option.votes += 1
    option.voters.append(g.user)
    db.session.commit()

    # Return updated poll
    return poll.serialize(), {"location": url_for("polls.get_poll", id=poll.id)}


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

    