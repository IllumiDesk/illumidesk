#  (C) Copyright IllumiDesk, LLC, 2020.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
#  the License. You may obtain a copy of the License at

#  http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
#  an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
#  specific language governing permissions and limitations under the License.

import logging
import os
import shutil
import sys

from secrets import token_hex

from flask import jsonify

from pathlib import Path

from illumidesk.grades.senders import LTIGradesSenderControlFile

from . import create_app
from .models import db
from .models import GraderService
from .grader_service import GraderServiceLauncher
from .grader_service import NB_UID
from .grader_service import NB_GID


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()


@app.route(
    '/control-file/<assignment_name>/<lis_outcome_service_url>/<lis_result_sourcedid>/<lms_user_id>/<course_id>',
    methods=['POST'],
)
def register_control_file(
    assignment_name: str, lis_outcome_service_url: str, lis_result_sourcedid: str, lms_user_id: str, course_id: str
):
    """
    Creates a new grades control file

    Args:
        assignment_name: string representation of the assignment name from the LMS (normalized)
        lis_outcome_service_url: url endpoint that is used to send grades to the LMS with LTI 1.1
        lis_result_sourcedid: unique assignment or module identifier used with LTI 1.1
        lms_user_id: unique (opaque) user id
        course_id: the course id within the lms

    Returns:
      JSON: True/False on whether or not the grader service was successfully launched

    example:
    ```
    {
        success: "True"
    }
    ```
    """
    # launcher = GraderServiceLauncher(org_name=org_name, course_id=course_id)
    # if not launcher.grader_deployment_exists():
    try:
        control_file = LTIGradesSenderControlFile(f'/home/grader-{course_id}/{course_id}')
        control_file.register_data(assignment_name, lis_outcome_service_url, lis_result_sourcedid, lms_user_id)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

    else:
        return jsonify(success=True)


@app.route('/services/<org_name>/<course_id>', methods=['POST'])
def launch(org_name: str, course_id: str):
    """
    Creates a new grader-notebook pod running as a JupyterHub unmanaged service if one does not exist.

    Args:
      org_name: the organization name
      course_id: the grader's course id

    Returns:
      JSON: True/False on whether or not the grader service was successfully launched

    example:
    ```
    {
        success: "True"
    }
    ```
    """
    # launcher = GraderServiceLauncher(org_name=org_name, course_id=course_id)
    # if not launcher.grader_deployment_exists():
    try:
        # launcher.create_grader_deployment()
        # Register the new service to local database
        new_service = GraderService(
            name=course_id,
            course_id=course_id,
            url=f'http://{course_id}:8888',
            api_token=token_hex(32),
        )
        db.session.add(new_service)
        db.session.commit()
        # then do patch for jhub deployment
        # with this the jhub pod will be restarted and get/load new services
        # launcher.update_jhub_deployment()
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

    else:
        return jsonify(success=False, message=f'A grader service already exists for this course_id:{course_id}'), 409


@app.route('/services', methods=['GET'])
def services():
    """
    Returns the grader-notebook list used as services defined in the JupyterHub config.

    Returns:
      JSON: a list of service dictionaries with the name and url and the groups associated
      to the grader service.

    example:
    ```
    {
        services: [{"name":"<course-id", "url": "http://grader-<course-id>:8888"...}],
        groups: {"formgrade-<course-id>": ["grader-<course-id>"] }
    }
    ```
    """
    services = GraderService.query.all()
    # format a json
    services_resp = []
    groups_resp = {}
    for s in services:
        services_resp.append(
            {
                'name': s.name,
                'url': s.url,
                'oauth_no_confirm': s.oauth_no_confirm,
                'admin': s.admin,
                'api_token': s.api_token,
            }
        )
        # add the jhub user group
        groups_resp.update({f'formgrade-{s.course_id}': [f'grader-{s.course_id}']})
    return jsonify(services=services_resp, groups=groups_resp)


@app.route("/services/<org_name>/<course_id>", methods=['DELETE'])
def services_deletion(org_name: str, course_id: str):
    """Deletes the grader setup service

    Args:
        org_name (str): the organization name
        course_id (str): the course id (label)

    Returns:
        JSON: True if the grader was successfully deleted false otherwise
    """
    launcher = GraderServiceLauncher(org_name=org_name, course_id=course_id)
    try:
        launcher.delete_grader_deployment()
        service_saved = GraderService.query.filter_by(course_id=course_id).first()
        if service_saved:
            db.session.delete(service_saved)
            db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@app.route("/courses/<org_name>/<course_id>/<assignment_name>", methods=['POST'])
def assignment_dir_creation(org_name: str, course_id: str, assignment_name: str):
    """Creates the directories required to manage assignments.

    Args:
        org_name (str): the organization name
        course_id (str): the course id (label)
        assignment_name (str): the assignment name

    Returns:
        JSON: True if the assignment directories were successfully created, false otherwise
    """
    launcher = GraderServiceLauncher(org_name=org_name, course_id=course_id)
    assignment_dir = os.path.abspath(Path(launcher.course_dir, 'source', assignment_name))
    if not os.path.isdir(assignment_dir):
        logger.info('Creating source dir %s for the assignment %s' % (assignment_dir, assignment_name))
        os.makedirs(assignment_dir)
    logger.info('Fixing folder permissions for %s' % assignment_dir)
    shutil.chown(str(Path(assignment_dir).parent), user=NB_UID, group=NB_GID)
    shutil.chown(str(assignment_dir), user=NB_UID, group=NB_GID)

    return jsonify(success=True)


@app.route("/healthcheck")
def healthcheck():
    """Healtheck endpoint

    Returns:
        JSON: True if the service is alive
    """
    return jsonify(success=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
