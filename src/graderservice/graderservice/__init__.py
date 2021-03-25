import os

from flask import Flask
from graderservice.models import db
from graderservice.routes import routes_blueprint

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(
    os.path.join(project_dir, "graderervice.db.sqlite3")
)


def create_app():
    """Creates the grader setup service as a Flask application using SQLite as the database with the SQLAlchemy ORM.

    Returns:
        flask_app: the Flask application object
    """
    app = Flask(__name__)
    app.register_blueprint(routes_blueprint)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_file
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.app_context().push()

    db.init_app(app)
    db.create_all()

    return app
