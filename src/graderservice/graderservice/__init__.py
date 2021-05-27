import logging
import os
from os import path

from flask import Flask
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists

from .models import db
from .routes import grader_setup_bp

log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging_config.ini")
logging.config.fileConfig(log_file_path)
logger = logging.getLogger()


grader_setup_db_host = os.environ.get("POSTGRES_GRADER_SETUP_HOST")
grader_setup_db_password = os.environ.get("POSTGRES_GRADER_SETUP_PASSWORD")
grader_setup_db_user = os.environ.get("POSTGRES_GRADER_SETUP_USER") or "postgres"
grader_setup_db_name = os.environ.get("ILLUMIDESK_K8S_NAMESPACE")

org_name = os.environ.get("ORGANIZATION_NAME") or "my-org"

if not org_name:
    raise EnvironmentError("ORGANIZATION_NAME env-var is not set")


project_dir = os.path.dirname(os.path.abspath(__file__))
database_uri = f"postgres://{grader_setup_db_user}:{grader_setup_db_password}@{grader_setup_db_host}:5432/gss_{grader_setup_db_name}"


def create_app():
    """Creates the grader setup service as a Flask application using SQLite as the database with the SQLAlchemy ORM.

    Returns:
        flask_app: the Flask application object
    """
    if not database_exists(database_uri):
        logger.debug("db not exist, create database")
        try:
            create_database(database_uri)
        except Exception as e:
            logger.error("Error creating database %s" % e)

    app = Flask(__name__)
    app.register_blueprint(grader_setup_bp)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.app_context().push()

    db.init_app(app)
    db.create_all()

    return app
