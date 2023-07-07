from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# App extensions
db = SQLAlchemy()
cors = CORS()


def create_app():
    # Configure app
    app = Flask(__name__)

    # Configure database
    from . import models
    app.config["SECRET_KEY"] = "secret_key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Configure routes
    from .users import users
    app.register_blueprint(users)
    from .polls import polls
    app.register_blueprint(polls)
    from .tokens import tokens
    app.register_blueprint(tokens)
    from .errors import errors
    app.register_blueprint(errors)

    # Configure CORS
    cors.init_app(app)

    return app
