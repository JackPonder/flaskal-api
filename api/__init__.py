from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import os

# App extensions
db = SQLAlchemy()
cors = CORS()


def create_app():
    # Configure app
    app = Flask(__name__)
    app.json.sort_keys = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI").replace("postgres://", "postgresql://")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    # Configure database
    from . import models
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
