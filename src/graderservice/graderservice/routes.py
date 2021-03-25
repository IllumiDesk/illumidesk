import logging
import os
import shutil
import sys
from pathlib import Path

from flask import Blueprint
from flask import jsonify
from graderservice.graderservice import NB_GID
from graderservice.graderservice import NB_UID
from graderservice.graderservice import GraderServiceLauncher
from graderservice.models import GraderService
from graderservice.models import db

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


routes_blueprint = Blueprint("routes", __name__)


@routes_blueprint.route("/services/path:<org_name>/path:<course_id>", methods=["POST"])
def launch(org_name: str, course_id: str):
    """
    Creates a new grader-notebook pod if not exists

    Args:
      org_name: the organization name
      course_id: the grader's course id (label)

    Returns:
      JSON: True/False on whether or not the grader service was successfully launched

    example:
    ```
    {
        success: "True"
    }
    ```
    """
    launcher = GraderServiceLauncher(org_name=org_name, course_id=course_id)
    if not launcher.grader_deployment_exists():
        try:
            launcher.create_grader_deployment()
            # Register the new service to local database
            with routes_blueprint.app_context():
                new_service = GraderService(
                    name=course_id,
                    course_id=course_id,
                    url=f"http://{launcher.grader_name}:8888",
                    api_token=launcher.grader_token,
                )
                db.session.add(new_service)
                db.session.commit()
            # then do patch for jhub deployment
            # with this the jhub pod will be restarted and get/load new services
            launcher.update_jhub_deployment()
            return jsonify(success=True)

        except Exception as e:
            return jsonify(success=False, message=str(e)), 500
    else:
        return (
            jsonify(
                success=False,
                message=f"A grader service already exists for this course_id:{course_id}",
            ),
            409,
        )


@routes_blueprint.route("/services", methods=["GET"])
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
                "name": s.name,
                "url": s.url,
                "oauth_no_confirm": s.oauth_no_confirm,
                "admin": s.admin,
                "api_token": s.api_token,
            }
        )
        # add the jhub user group
        groups_resp.update({f"formgrade-{s.course_id}": [f"grader-{s.course_id}"]})
    return jsonify(services=services_resp, groups=groups_resp)


@routes_blueprint.route(
    "/services/path:<org_name>/path:<course_id>", methods=["DELETE"]
)
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
            with routes_blueprint.app_context():
                db.session.delete(service_saved)
                db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@routes_blueprint.route(
    "/courses/<org_name>/<course_id>/<assignment_name>", methods=["POST"]
)
def assignment_dir_creation(org_name: str, course_id: str, assignment_name: str):
    """Creates the directories required to manage assignments.

    Args:
        org_name: the organization name
        course_id: the course id (label)
        assignment_name: the assignment name

    Returns:
        JSON: True if the assignment directories were successfully created, false otherwise
    """
    launcher = GraderServiceLauncher(org_name=org_name, course_id=course_id)
    assignment_dir = os.path.abspath(
        Path(launcher.course_dir, "source", assignment_name)
    )
    if not os.path.isdir(assignment_dir):
        logger.info(
            "Creating source dir %s for the assignment %s"
            % (assignment_dir, assignment_name)
        )
        os.makedirs(assignment_dir)
    logger.info("Fixing folder permissions for %s" % assignment_dir)
    shutil.chown(str(Path(assignment_dir).parent), user=NB_UID, group=NB_GID)
    shutil.chown(str(assignment_dir), user=NB_UID, group=NB_GID)

    return jsonify(success=True)


@routes_blueprint.route("/healthcheck")
def healthcheck():
    """Healtheck endpoint

    Returns:
        JSON: True if the service is alive
    """
    return jsonify(success=True)
