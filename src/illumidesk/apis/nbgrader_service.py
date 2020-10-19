import logging
import os
from pathlib import Path
import shutil

from illumidesk.authenticators.utils import LTIUtils

from nbgrader.api import Assignment
from nbgrader.api import Course
from nbgrader.api import Gradebook
from nbgrader.api import InvalidEntry

from sqlalchemy_utils import database_exists
from sqlalchemy_utils import create_database


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


nbgrader_db_host = os.environ.get('POSTGRES_NBGRADER_HOST')
nbgrader_db_port = os.environ.get('POSTGRES_NBGRADER_PORT') or 5432
nbgrader_db_password = os.environ.get('POSTGRES_NBGRADER_PASSWORD')
nbgrader_db_user = os.environ.get('POSTGRES_NBGRADER_USER')

org_name = os.environ.get('ORGANIZATION_NAME') or 'my-org'

if not org_name:
    raise EnvironmentError('ORGANIZATION_NAME env-var is not set')


def nbgrader_format_db_url(course_id: str) -> str:
    """
    Returns the nbgrader database url with the format: <org_name>_<course-id>

    Args:
      course_id: the course id (usually associated with the course label) from which the launch was initiated.
    """
    course_id = LTIUtils().normalize_string(course_id)
    database_name = f'{org_name}_{course_id}'
    return (
        f'postgresql://{nbgrader_db_user}:{nbgrader_db_password}@{nbgrader_db_host}:{nbgrader_db_port}/{database_name}'
    )


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

    def __init__(self, course_id: str, check_database_exists: bool = False):
        if not course_id:
            raise ValueError('course_id missing')

        self.course_id = LTIUtils().normalize_string(course_id)
        self.course_dir = f'/home/grader-{self.course_id}/{self.course_id}'
        self.uid = int(os.environ.get('NB_GRADER_UID') or '10001')
        self.gid = int(os.environ.get('NB_GID') or '100')

        self.db_url = nbgrader_format_db_url(course_id)
        self.database_name = f'{org_name}_{self.course_id}'
        if check_database_exists:
            self.create_database_if_not_exists()

    def create_database_if_not_exists(self) -> None:
        """Creates a new database if it doesn't exist"""
        conn_uri = nbgrader_format_db_url(self.course_id)

        if not database_exists(conn_uri):
            logger.debug("db not exist, create database")
            create_database(conn_uri)

    def add_user_to_nbgrader_gradebook(self, username: str, lms_user_id: str) -> None:
        """
        Adds a user to the nbgrader gradebook database for the course.

        Args:
            username: The user's username
            lms_user_id: The user's id on the LMS
        Raises:
            InvalidEntry: when there was an error adding the user to the database
        """
        if not username:
            raise ValueError('username missing')
        if not lms_user_id:
            raise ValueError('lms_user_id missing')

        with Gradebook(self.db_url, course_id=self.course_id) as gb:
            try:
                gb.update_or_create_student(username, lms_user_id=lms_user_id)
                logger.debug('Added user %s with lms_user_id %s to gradebook' % (username, lms_user_id))
            except InvalidEntry as e:
                logger.debug('Error during adding student to gradebook: %s' % e)

    def update_course(self, **kwargs) -> None:
        """
        Updates the course in nbgrader database
        """
        with Gradebook(self.db_url, course_id=self.course_id) as gb:
            gb.update_course(self.course_id, **kwargs)

    def get_course(self) -> Course:
        """
        Gets the course model instance
        """
        with Gradebook(self.db_url, course_id=self.course_id) as gb:
            course = gb.check_course(self.course_id)
            logger.debug(f'course got from db:{course}')
            return course

    def create_assignment_in_nbgrader(self, assignment_name: str, **kwargs: dict) -> Assignment:
        """
        Adds an assignment to nbgrader database

        Args:
            assignment_name: The assingment's name
        Raises:
            InvalidEntry: when there was an error adding the assignment to the database
        """
        if not assignment_name:
            raise ValueError('assignment_name missing')
        assignment_name = LTIUtils().normalize_string(assignment_name)
        logger.debug('Assignment name normalized %s to save in gradebook' % assignment_name)
        assignment = None
        with Gradebook(self.db_url, course_id=self.course_id) as gb:
            try:
                assignment = gb.update_or_create_assignment(assignment_name, **kwargs)
                logger.debug('Added assignment %s to gradebook' % assignment_name)
                assignment_dir = os.path.abspath(Path(self.course_dir, 'source', assignment_name))
                if not os.path.isdir(assignment_dir):
                    logger.debug('Creating source dir %s for the assignment %s' % (assignment_dir, assignment_name))
                    os.makedirs(assignment_dir)
                logger.debug('Fixing folder permissions for %s' % assignment_dir)
                shutil.chown(str(Path(assignment_dir).parent), user=self.uid, group=self.gid)
                shutil.chown(str(assignment_dir), user=self.uid, group=self.gid)
            except InvalidEntry as e:
                logger.debug('Error ocurred by adding assignment to gradebook: %s' % e)
        return assignment
