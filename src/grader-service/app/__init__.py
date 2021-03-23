#  (C) Copyright IllumiDesk, LLC, 2020.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
#  the License. You may obtain a copy of the License at

#  http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
#  an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
#  specific language governing permissions and limitations under the License.

import os

from flask import Flask

from .models import db

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(
    os.path.join(project_dir, "gradersetup.db.sqlite3")
)


def create_app():
    """Creates the grader setup service as a Flask application using SQLite as the database with the SQLAlchemy ORM.

    Returns:
        flask_app: the Flask application object
    """
    flask_app = Flask(__name__)
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = database_file
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.app_context().push()
    db.init_app(flask_app)
    db.create_all()
    return flask_app
