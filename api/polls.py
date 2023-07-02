from flask import Blueprint, url_for, abort, request

from . import db
from .models import User, Poll, PollOption, Comment

polls = Blueprint("polls", __name__)


@polls.route("/polls", methods=["POST"])
def create():
    """Create a new poll"""

    # Ensure correct data was submitted
    json = request.get_json()
    if type(json) != dict: 
        abort(400, description="Invalid data")
    creator = db.session.get(User, json.get("creatorId"))
    title = json.get("title")
    options = json.get("options")
    tag = json.get("tag")
    if not creator or not title or type(options) != list or len(options) < 2:
        abort(400, description="Invalid data")

    # Add new poll to database
    new_poll = Poll(creator=creator, title=title, tag=tag)
    db.session.add(new_poll)
    for option in options:
        if not option:
            continue
        new_option = PollOption(poll=new_poll, name=option)
        db.session.add(new_option)
    db.session.commit()

    # Return newly created poll
    return new_poll.serialize(), 201, {"location": url_for("polls.get", id=new_poll.id)}


@polls.route("/polls/<int:id>/comments", methods=["POST"])
def comment(id: int):
    """Create a new comment on a specified poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id) or abort(404, description="No poll was found for the specified id")

    # Ensure correct data was submitted
    json = request.get_json()
    if type(json) != dict: 
        abort(400, description="Invalid data")
    creator = db.session.get(User, json.get("creatorId"))
    content = json.get("content")
    if not creator or not content:
        abort(400, description="Invalid data")
    
    # Add new comment to the database
    new_comment = Comment(creator=creator, poll=poll, content=content)
    db.session.add(new_comment)
    db.session.commit()

    # Return newly created comment
    return new_comment.serialize(), 201


@polls.route("/polls", methods=["GET"])
def all():
    """Get a collection of polls"""

    # Query database for polls
    polls = db.session.query(Poll)

    # Filter according to query parameter
    tag = request.args.get("tag")
    if tag:
        polls = polls.filter_by(tag=tag)

    return [poll.serialize() for poll in polls.all()]


@polls.route("/polls/<int:id>", methods=["GET"])
def get(id: int):
    """Get a poll by its id"""
    
    # Query database for poll
    poll = db.session.get(Poll, id) or abort(404, description="No poll was found for the specified id")
    
    return poll.serialize()


@polls.route("/polls/<int:id>/comments", methods=["GET"])
def comments(id: int):
    """Get a collection of comments on a specified poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id) or abort(404, description="No poll was found for the specified id")
    
    return [comment.serialize() for comment in poll.comments]


@polls.route("/polls/<int:id>/vote", methods=["PATCH"])
def vote(id: int):
    """Submit a vote for a poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id) or abort(404, description="No poll was found for the specified id")
    
    # Ensure correct data was submitted
    json = request.get_json()
    if type(json) != dict: 
        abort(400, description="Invalid data")
    voter = db.session.get(User, json.get("voterId"))
    option = db.session.get(PollOption, json.get("vote"))
    if not voter or not option or option not in poll.options:
        abort(400, description="Invalid form data")
    
    # Ensure voter has not already voted on this poll
    if voter in poll.get_all_voters():
        abort(400, description="User has already voted on this poll")
        
    # Update poll with new vote
    option.votes += 1
    option.voters.append(voter)
    db.session.commit()

    # Return updated poll
    return poll.serialize(), {"location": url_for("polls.get", id=poll.id)}
