from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error(status_code = 400, message = None):
    """Return an error"""

    data = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown Error")}
    if message:
        data["message"] = message

    reponse = jsonify(data)
    reponse.status_code = status_code
    return reponse
