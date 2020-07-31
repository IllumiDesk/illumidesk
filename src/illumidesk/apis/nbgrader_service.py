import logging
from pathlib import Path
import os
import shutil
import sys

from nbgrader.api import Gradebook
from nbgrader.api import InvalidEntry

from tornado.httpclient import HTTPResponse

from typing import Awaitable


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class NbGraderServiceHelper:
    def __init__(self, course_id: str):
        if not course_id:
            raise ValueError('course_id missing')
        self.course_id = course_id
        self.uid = int(os.environ.get('NB_UID') or '10001')
        self.gid = int(os.environ.get('NB_GID') or '100')
        grader_name = f'grader-{course_id}'
        self.course_dir = f'/home/{grader_name}/{course_id}'

        self.gradebook_path = Path(self.course_dir, 'gradebook.db')
        # make sure the gradebook path exists
        self.gradebook_path.parent.mkdir(exist_ok=True, parents=True)   
        logger.debug('Gradebook path is %s' % self.gradebook_path)
        logger.debug("creating gradebook instance")
        self.gb = Gradebook(f'sqlite:///{self.gradebook_path}', course_id=self.course_id)
        logger.debug(
            'Changing or making sure the gradebook directory permissions (with path %s) to %s:%s ' % (self.gradebook_path, self.uid, self.gid)
        )
        shutil.chown(str(self.gradebook_path), user=self.uid, group=self.gid)


    async def create_assignment_in_nbgrader(
        self, assignment_name: str, lms_resource_link_id: str, **kwargs: dict
    ) -> Awaitable['HTTPResponse']:
        """
        Adds an assignment to nbgrader database

        Args:           
            assignment_name: The assingment's name
        Raises:
            InvalidEntry: when there was an error adding the assignment to the database
        """
        if not assignment_name:
            raise ValueError('assignment_name missing')
        if not lms_resource_link_id:
            raise ValueError('lms_resource_link_id missing')
        try:
            self.gb.update_or_create_assignment(assignment_name, lms_resource_link_id=lms_resource_link_id, **kwargs)
            logger.debug('Added assignment %s with lms_resource_link_id %s to gradebook' % (assignment_name, lms_resource_link_id))
            sourcedir = os.path.abspath(Path(self.course_dir, 'source', assignment_name))
            if not os.path.isdir(sourcedir):
                logger.debug('Creating source dir %s for the assignment %s' % (sourcedir, assignment_name))
                os.makedirs(sourcedir)
            logger.debug('Fixing folder permissions for %s' % sourcedir)
            shutil.chown(str(sourcedir), user=self.uid, group=self.gid)
        except InvalidEntry as e:
            logger.debug('Error during adding assignment to gradebook: %s' % e)
        self.gb.close()
