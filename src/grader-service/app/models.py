#  (C) Copyright IllumiDesk, LLC, 2020.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
#  the License. You may obtain a copy of the License at

#  http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
#  an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
#  specific language governing permissions and limitations under the License.

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class GraderService(db.Model):
    """Base model for the grader setup service that inherits from the base SQLAlchemy Model class.

    Attrs:
        id: the grader setup service primary key
        name: the grader setup service name
        course_id: the course id (label) referenced when calling services
        url: the grader setup service's URL (endpoint)
        admin: admin priviledges as defined by the JupyterHub's services configuration option
        api_token: the token used to access the JupyterHub so that it is run as an externally managed service

    Returns:
        The grader Service object's name and url properties
    """

    __tablename__ = "grader_services"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    course_id = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    oauth_no_confirm = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=True)
    api_token = db.Column(db.String(150), nullable=True)

    def get_id(self):
        """Return the service ID as a unicode string (`str`)."""
        return str(self.id)

    def __repr__(self):
        return "<Service name: {} at {}>".format(self.name, self.url)
