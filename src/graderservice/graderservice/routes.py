import logging.config
import os
import shutil
from os import path
from pathlib import Path

from flask import Blueprint
from flask import jsonify

from .graderservice import NB_GID
from .graderservice import NB_UID
from .graderservice import GraderServiceLauncher
from .models import GraderService
from .models import db

log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging_config.ini")
logging.config.fileConfig(log_file_path)
logger = logging.getLogger()


grader_setup_bp = Blueprint("grader_setup_bp", __name__)


@grader_setup_bp.route("/services/<org_name>/<course_id>", methods=["POST"])
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
            logger.info(
                "Creating grader deployment for org %s and course %s"
                % (org_name, course_id)
            )
            # Register the new service to local database
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
            return jsonify(
                success=True,
                message=f"Created new grader service for: {course_id}",
            )

        except Exception as e:
            logger.error("Exception when calling create_grader_deployment() %s" % e)
            return jsonify(success=False, message=str(e)), 500
    else:
        logger.info("A grader service exists for the course_id %s" % course_id)
        return (
            jsonify(
                success=False,
                message=f"A grader service already exists for this course_id:{course_id}",
            ),
            409,
        )


@grader_setup_bp.route("/services", methods=["GET"])
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
        logger.debug(
            "Adding formgrade-%s and grader-%s to response" % (s.course_id, s.course_id)
        )
    logger.info("Services response %s and %s" % (services_resp, groups_resp))
    return jsonify(services=services_resp, groups=groups_resp)


@grader_setup_bp.route("/services/<org_name>/<course_id>", methods=["DELETE"])
def services_deletion(org_name: str, course_id: str):
    """Deletes the grader setup service

    Args:
        org_name: the organization name
        course_id: the course id (label)

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
        logger.info("Deleted grader service for course %s:" % course_id)
        return jsonify(
            success=True,
            message=f"Deleted grader service for course: {course_id}",
        )
    except Exception as e:
        logger.error("Exception when calling delete_grader_deployment(): %s" % e)
        return jsonify(success=False, error=str(e)), 500


@grader_setup_bp.route(
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
        try:
            os.makedirs(assignment_dir)
        except Exception as e:
            logger.error("Exception when making assignmen directory: %s" % e)
    try:
        shutil.chown(str(Path(assignment_dir).parent), user=NB_UID, group=NB_GID)
        logger.debug(
            f"Updating permissions for {str(Path(assignment_dir).parent)} with {NB_UID} and {NB_GID}"
        )
        shutil.chown(str(assignment_dir), user=NB_UID, group=NB_GID)
        logger.debug(f"Creating new assignment directory {assignment_dir} OK")
    except Exception as e:
        logger.error(f"Exception when updating assignment directory permissions: {e}")
    logger.info("Creating new assignment directory %s OK" % assignment_dir)
    return jsonify(
        success=True,
        message=f"Created new assignment directory: {assignment_dir}",
    )


@grader_setup_bp.route("/healthcheck")
def healthcheck():
    """Healtheck endpoint

    Returns:
        JSON: True if the service is alive
    """
    logger.debug("Health check reponse OK")
    return jsonify(success=True)
