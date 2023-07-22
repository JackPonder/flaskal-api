from flask import Blueprint
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(HTTPException)
def http_error(error: HTTPException):
    return {
        "code": error.code,
        "message": error.name,
        "description": error.description
    }, error.code


@errors.app_errorhandler(SQLAlchemyError)
def sqlalchemy_error(error: SQLAlchemyError):
    return {
        "code": 500,
        "message": "SQLAlchemy Error", 
        "description": str(error)
    }, 500
