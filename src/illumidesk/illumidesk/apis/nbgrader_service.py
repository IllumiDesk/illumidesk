import logging
import os

from nbgrader.api import Assignment
from nbgrader.api import Course
from nbgrader.api import Gradebook
from nbgrader.api import InvalidEntry

from illumidesk.authenticators.utils import LTIUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


nbgrader_db_host = os.environ.get("POSTGRES_NBGRADER_HOST")
nbgrader_db_port = os.environ.get("POSTGRES_NBGRADER_PORT") or 5432
nbgrader_db_password = os.environ.get("POSTGRES_NBGRADER_PASSWORD")
nbgrader_db_user = os.environ.get("POSTGRES_NBGRADER_USER")
nbgrader_db_name = os.environ.get("POSTGRES_NBGRADER_DATABASE")
mnt_root = os.environ.get("ILLUMIDESK_MNT_ROOT", "/illumidesk-courses")

org_name = os.environ.get("ORGANIZATION_NAME") or "my-org"

if not org_name:
    raise EnvironmentError("ORGANIZATION_NAME env-var is not set")

CAMPUS_ID = os.environ.get("CAMPUS_ID")
if not CAMPUS_ID:
    raise EnvironmentError("CAMPUS_ID env-var is not set")

def nbgrader_format_db_url() -> str:
    """
    Returns the nbgrader database url
    """
    return f"postgresql://{nbgrader_db_user}:{nbgrader_db_password}@{nbgrader_db_host}:{nbgrader_db_port}/{nbgrader_db_name}"


class NbGraderServiceHelper:
    """
    Helper class to use the nbgrader database and gradebook

    Attrs:
      course_id: the course id (equivalent to the course name)
      course_dir: the course directory located in the grader home directory
      uid: the user id that owns the grader home directory
      gid: the group id that owns the grader home directory
      db_url: the database string connection uri
      database_name: the database name
    """

    def __init__(self, course_id: str):
        if not course_id:
            raise ValueError("course_id missing")

        self.course_id = LTIUtils().normalize_string(course_id)
        self.course_dir = (
            f"{mnt_root}/{org_name}/home/grader-{self.course_id}/{self.course_id}"
        )
        self.uid = int(os.environ.get("NB_GRADER_UID") or "10001")
        self.gid = int(os.environ.get("NB_GRADER_GID") or "100")

        self.db_url = nbgrader_format_db_url()

    def add_user_to_nbgrader_gradebook(self, email: str, external_user_id: str, source: str, source_type: str, role_name: str = None) -> None:
        """
        Adds a user to the nbgrader gradebook database for the course.

        Args:
            email: The user's email
            external_user_id: The user's id on the external system
            source: source from where user was authenticated
            source_type: source_type
            role_name: role of the user
        Raises:
            InvalidEntry: when there was an error adding the user to the database
        """
        if not email:
            raise ValueError("email missing")
        if not external_user_id:
            raise ValueError("external_user_id missing")

        with Gradebook(self.db_url, course_id=self.course_id, campus_id=CAMPUS_ID) as gb:
            try:
                user = gb.update_or_create_user_by_email(email, role_name=role_name, external_user_id=external_user_id, source=source, source_type=source_type)
                logger.debug(
                    "Added user %s with external_user_id %s to gradebook"
                    % (email, external_user_id)
                )
                return user.to_dict()
            except InvalidEntry as e:
                logger.debug("Error during adding student to gradebook: %s" % e)

    def update_course(self, **kwargs) -> None:
        """
        Updates the course in nbgrader database
        """
        with Gradebook(self.db_url, course_id=self.course_id, campus_id=CAMPUS_ID) as gb:
            gb.update_course(self.course_id, **kwargs)

    def get_course(self) -> Course:
        """
        Gets the course model instance
        """
        with Gradebook(self.db_url, course_id=self.course_id, campus_id=CAMPUS_ID) as gb:
            course = gb.check_course(self.course_id)
            logger.debug(f"course got from db:{course}")
            return course

    def register_assignment(self, assignment_name: str, **kwargs: dict) -> Assignment:
        """
        Adds an assignment to nbgrader database

        Args:
            assignment_name: The assingment's name
        Raises:
            InvalidEntry: when there was an error adding the assignment to the database
        """
        if not assignment_name:
            raise ValueError("assignment_name missing")
        logger.debug(
            "Assignment name normalized %s to save in gradebook" % assignment_name
        )
        assignment = None
        with Gradebook(self.db_url, course_id=self.course_id, campus_id=CAMPUS_ID) as gb:
            try:
                assignment = gb.update_or_create_assignment(assignment_name, **kwargs)
                logger.debug("Added assignment %s to gradebook" % assignment_name)
            except InvalidEntry as e:
                logger.debug("Error ocurred by adding assignment to gradebook: %s" % e)
        return assignment
