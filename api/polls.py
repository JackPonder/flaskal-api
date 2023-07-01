from flask import Blueprint, jsonify, url_for, request

from . import db
from .models import User, Poll, PollOption, Comment
from .errors import error_response

polls = Blueprint("polls", __name__)


@polls.route("/polls", methods=["POST"])
def create():
    """Create a new poll"""

    # Ensure correct data was submitted
    json = request.get_json() or {}
    creator = db.session.get(User, json.get("creatorId"))
    title = json.get("title")
    options = json.get("options")
    tag = json.get("tag")
    if not creator or not title or type(options) != list or len(options) < 2:
        return error_response(message="invalid form data")

    # Add new poll to database
    new_poll = Poll(creator=creator, title=title)
    if tag:
        new_poll.tag = tag
    db.session.add(new_poll)
    for option in options:
        if not option:
            continue
        new_option = PollOption(poll=new_poll, name=option)
        db.session.add(new_option)
    db.session.commit()

    # Return newly created poll
    response = jsonify(new_poll.serialize())
    response.status_code = 201
    response.headers["Location"] = url_for("polls.get", id=new_poll.id)
    return response


@polls.route("/polls/<int:id>/comments", methods=["POST"])
def comment(id: int):
    """Create a new comment on a specified poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)

    # Return an error if no poll was found
    if not poll:
        return error_response(404, "invalid poll id")

    # Ensure correct data was submitted
    json = request.get_json() or {}
    creator = db.session.get(User, json.get("creatorId"))
    content = json.get("content")
    if not creator or not content:
        return error_response(message="invalid form data")
    
    # Add new comment to the database
    new_comment = Comment(creator=creator, poll=poll, content=content)
    db.session.add(new_comment)
    db.session.commit()

    # Return newly created comment
    response = jsonify(new_comment.serialize())
    response.status_code = 201
    return response


@polls.route("/polls", methods=["GET"])
def all():
    """Get a collection of polls"""

    # Query database for polls
    polls = db.session.query(Poll).all()

    # Filter according to query parameter
    tag = request.args.get("tag")
    if tag:
        polls = [poll for poll in polls if poll.tag == tag]

    return jsonify([poll.serialize() for poll in polls])


@polls.route("/polls/<int:id>", methods=["GET"])
def get(id: int):
    """Get a poll by its id"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)

    # Return an error if no poll was found
    if not poll:
        return error_response(404, "invalid poll id")
    
    return jsonify(poll.serialize())


@polls.route("/polls/<int:id>/comments", methods=["GET"])
def comments(id: int):
    """Get a collection of comments on a specified poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)

    # Return an error if no poll was found
    if not poll:
        return error_response(404, "invalid poll id")
    
    return jsonify([comment.serialize() for comment in poll.comments])


@polls.route("/polls/<int:id>/vote", methods=["PATCH"])
def vote(id: int):
    """Submit a vote for a poll"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)

    # Return an error if no poll was found
    if not poll:
        return error_response(404, "invalid poll id")
    
    # Ensure correct data was submitted
    json = request.get_json() or {}
    voter = db.session.get(User, json.get("voterId"))
    option = db.session.get(PollOption, json.get("vote"))
    if not voter or not option or option not in poll.options:
        return error_response(message="invalid form data")
    
    # Ensure voter has not already voted on this poll
    if voter.id in poll.get_all_voters():
        return error_response(message="user has already voted on this poll")
        
    # Update poll with new vote
    option.votes += 1
    option.voters.append(voter)
    db.session.commit()

    # Return updated poll
    response = jsonify(poll.serialize())
    response.headers["Location"] = url_for("polls.get", id=poll.id)
    return response
