import logging
from pathlib import Path
import os
import shutil
import sys

from nbgrader.api import Assignment, Course, Gradebook
from nbgrader.api import InvalidEntry

from illumidesk.authenticators.utils import LTIUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NbGraderServiceHelper:
    def __init__(self, course_id: str):
        if not course_id:
            raise ValueError('course_id missing')

        self.course_id = LTIUtils().normalize_string(course_id)
        self.uid = int(os.environ.get('NB_UID') or '10001')
        self.gid = int(os.environ.get('NB_GID') or '100')
        grader_name = f'grader-{course_id}'
        self.course_dir = f'/home/{grader_name}/{course_id}'
        self.gradebook_path = Path(self.course_dir, 'gradebook.db')
        # make sure the gradebook path exists
        self.gradebook_path.parent.mkdir(exist_ok=True, parents=True)
        logger.debug('Gradebook path is %s' % self.gradebook_path)
        logger.debug("creating gradebook instance")
        
        logger.debug(
            'Changing or making sure the gradebook directory permissions (with path %s) to %s:%s '
            % (self.gradebook_path, self.uid, self.gid)
        )
        shutil.chown(str(self.gradebook_path), user=self.uid, group=self.gid)

    def update_course(self, **kwargs) -> None:
        with Gradebook(f'sqlite:///{self.gradebook_path}', course_id=self.course_id) as gb:
            gb.update_course(self.course_id, **kwargs)

    def get_course(self) -> Course:
        with Gradebook(f'sqlite:///{self.gradebook_path}', course_id=self.course_id) as gb:
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
        with Gradebook(f'sqlite:///{self.gradebook_path}', course_id=self.course_id) as gb:
            try:
                assignment = gb.update_or_create_assignment(assignment_name, **kwargs)
                logger.debug('Added assignment %s to gradebook' % assignment_name)
                sourcedir = os.path.abspath(Path(self.course_dir, 'source', assignment_name))
                if not os.path.isdir(sourcedir):
                    logger.debug('Creating source dir %s for the assignment %s' % (sourcedir, assignment_name))
                    os.makedirs(sourcedir)
                logger.debug('Fixing folder permissions for %s' % sourcedir)
                shutil.chown(str(sourcedir), user=self.uid, group=self.gid)
            except InvalidEntry as e:
                logger.debug('Error during adding assignment to gradebook: %s' % e)
        return assignment
