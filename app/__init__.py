from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# App extensions
db = SQLAlchemy()


def create_app():
    # Configure app
    app = Flask(__name__)

    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    db.init_app(app)

    # Configure routes
    from app.routes import routes
    app.register_blueprint(routes)

    # Configure models
    from .models import User
    with app.app_context():
        db.create_all()

    return app
