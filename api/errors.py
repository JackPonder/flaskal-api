from flask import Blueprint
from werkzeug.exceptions import HTTPException

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(HTTPException)
def error_response(error):
    return {
        "code": error.code,
        "message": error.name,
        "description": error.description
    }, error.code
