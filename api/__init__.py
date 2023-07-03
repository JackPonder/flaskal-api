from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# App extensions
db = SQLAlchemy()


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
    from .errors import errors
    app.register_blueprint(errors)

    return app
