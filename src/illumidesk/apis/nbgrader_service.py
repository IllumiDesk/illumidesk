import logging
from pathlib import Path
import os
import shutil

from nbgrader.api import Assignment, Course, Gradebook
from nbgrader.api import InvalidEntry

from illumidesk.authenticators.utils import LTIUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


PG_DB_FORMAT = 'postgresql://{user}:{password}@{host}/{db}'


class NbGraderServiceBaseHelper:
    def __init__(self, course_id: str):
        if not course_id:
            raise ValueError('course_id missing')

        self.course_id = LTIUtils().normalize_string(course_id)
        self.db_url = ''
        grader_name = f'grader-{self.course_id}'
        self.course_dir = f'/home/{grader_name}/{self.course_id}'
        self.uid = int(os.environ.get('NB_UID') or '10001')
        self.gid = int(os.environ.get('NB_GID') or '100')

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


class NbGraderServicePostgresHelper(NbGraderServiceBaseHelper):
    """
    Helper class to use nbgrader with postgres
    For postgres the database must be created before. Nbgrader will execute the migration scripts
    only if the database exists and it does not contain the tables
    """

    def __init__(self, course_id: str):
        super(NbGraderServicePostgresHelper, self).__init__(course_id)
        self.org_name = os.environ.get('ORGANIZATION_NAME') or 'my-org'

        # get DATABASE_URL FROM ENV-VARS
        self.db_user = os.environ.get('POSTGRES_USER')
        self.db_password = os.environ.get('POSTGRES_PASSWORD')
        self.db_host = os.environ.get('POSTGRES_HOST')
        # normalize org_name to be used as db_name
        self.db_name = 'nb_' + self.org_name.lower().replace('-', '_').replace(' ', '_')

        self.db_url = PG_DB_FORMAT.format(
            user=self.db_user, password=self.db_password, host=self.db_host, db=self.db_name
        )


class NbGraderServiceSQLiteHelper(NbGraderServiceBaseHelper):
    """
    Helper class to use nbgrader with sqlite
    With sqlite the database file is created automatically
    """

    def __init__(self, course_id: str):
        super(NbGraderServiceSQLiteHelper, self).__init__(course_id)

        self.gradebook_path = Path(self.course_dir, 'gradebook.db')
        # make sure the gradebook path exists
        self.gradebook_path.parent.mkdir(exist_ok=True, parents=True)
        logger.debug('Gradebook path is %s' % self.gradebook_path)
        logger.debug("Creating gradebook instance")
        self.db_url = f'sqlite:///{self.gradebook_path}'
        # With new Gradebook instance the database is initiated/created
        with Gradebook(self.db_url, course_id=self.course_id):
            logger.debug(
                'Changing gradebook directory permissions (with path %s) to %s:%s '
                % (self.gradebook_path, self.uid, self.gid)
            )
            shutil.chown(str(self.gradebook_path), user=self.uid, group=self.gid)
