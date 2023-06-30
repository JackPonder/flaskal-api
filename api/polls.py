from flask import Blueprint, jsonify, url_for, request

from . import db
from .models import User, Poll, PollOption
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


@polls.route("/polls/<int:id>", methods=["GET"])
def get(id: int):
    """Get a poll by its id"""
    
    # Query database for poll
    poll = db.session.get(Poll, id)

    # Return an error if no poll was found
    if not poll:
        return error_response(404, "invalid poll id")
    
    return jsonify(poll.serialize())


@polls.route("/polls", methods=["GET"])
def get_all():
    """Get a collection of polls"""

    # Query database for polls
    polls = db.session.query(Poll).all()

    return jsonify([poll.serialize() for poll in polls])


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
