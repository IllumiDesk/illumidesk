import json
import logging
import os

from filelock import FileLock
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LTIGradesSenderControlFile:
    """
    Control file to register assignment information about grades submission (only for LTI 1.1).
    With this file we can associate assignments that come from lms and those that teachers create on the nbgrader console

    Args:
        course_dir (str): Course directory, normally where the gradebook is (/home/grader-<course-id>/<course-id>)
    """

    # TODO: re-think to centralize files like this or replace all of them with a little DB (sqlite)
    FILE_NAME = 'lti_grades_sender_assignments.json'
    FILE_LOADED = False
    lock_file = 'grades-sender.lock'
    cache_sender_data = {}

    def __init__(self, course_dir: str):
        self.config_path = course_dir
        if not LTIGradesSenderControlFile.FILE_LOADED:
            logger.debug('The control file cache will be loaded from filesystem...')
            # try to read first time
            self._loadFromFile()

    @property
    def config_fullname(self):
        return os.path.join(self.config_path, LTIGradesSenderControlFile.FILE_NAME)

    def initialize_control_file(self) -> None:
        with FileLock(LTIGradesSenderControlFile.lock_file):
            with Path(self.config_fullname).open('w+') as new_file:
                json.dump(LTIGradesSenderControlFile.cache_sender_data, new_file)
                logger.debug('Control file initialized.')

    def _loadFromFile(self) -> None:
        # TODO: apply a file lock
        if not Path(self.config_fullname).exists() or Path(self.config_fullname).stat().st_size == 0:
            self.initialize_control_file()
        else:
            with Path(self.config_fullname).open('r') as file:
                try:
                    LTIGradesSenderControlFile.cache_sender_data = json.load(file)
                    logger.debug(f'Control file found and loaded from:{self.config_fullname}')
                    logger.info(f'Control file content:{LTIGradesSenderControlFile.cache_sender_data}')
                except json.JSONDecodeError as e:
                    logger.error(f'Error reading the control file:{e}')
                    if Path(self.config_fullname).stat().st_size != 0:
                        logger.error(f'Control file with wrong format:{e}. It will be initialized instead')
                        self.initialize_control_file()

        LTIGradesSenderControlFile.FILE_LOADED = True

    def register_data(
        self, assignment_name: str, lis_outcome_service_url: str, lms_user_id: str, lis_result_sourcedid: str
    ) -> None:
        """
        Registers some information about where the assignment grades are sent: like the url, sourcedid.
        This information is used later when the teacher finishes its work in nbgrader console

        Args:
            assignment_name:
                This value must be the same as nbgrader assigment name
            lis_outcome_service_url:
                Obtained from lti authentication request ('lis_outcome_service_url'). This url is used to send grades
            lms_user_id:
                Obtained from lti authentication request ('user_id'). this Id identifies the student in lms and nbgrader
            lis_result_sourcedid:
                Obtained from lti authentication request ('lis_result_sourcedid'). It's value is unique for each student
        """
        logger.info(f'Registering data in grades-sender control file for assignment name: {assignment_name}')
        logger.info(f'lis_outcome_service_url received: {lis_outcome_service_url}')
        logger.info(f'lms_user_id received: {lms_user_id}')
        logger.info(f'lis_result_sourcedid received: {lis_result_sourcedid}')

        assignment_reg = None
        # if the assignment does not exist then register it
        with FileLock(LTIGradesSenderControlFile.lock_file):
            if assignment_name not in LTIGradesSenderControlFile.cache_sender_data:
                # it's a new assignment
                assignment_reg = {
                    'lis_outcome_service_url': lis_outcome_service_url,
                    'students': [],
                }
            else:
                assignment_reg = LTIGradesSenderControlFile.cache_sender_data[assignment_name]

            # if the student info not exists then create it
            if not [student for student in assignment_reg['students'] if student['lms_user_id'] == lms_user_id]:
                assignment_reg['students'].append(
                    {'lms_user_id': lms_user_id, 'lis_result_sourcedid': lis_result_sourcedid}
                )
                # only if a new assignment/student info was included save the file
                self._write_new_assignment_info(assignment_name, assignment_reg)

    def _write_new_assignment_info(self, assignment_name: str, data: dict) -> None:
        # append new info
        LTIGradesSenderControlFile.cache_sender_data[assignment_name] = data
        # save the file to disk
        with Path(self.config_fullname).open('r+') as file:
            json.dump(LTIGradesSenderControlFile.cache_sender_data, file)

    def get_assignment_by_name(self, assignment_name: str) -> None:
        if assignment_name in LTIGradesSenderControlFile.cache_sender_data:
            return LTIGradesSenderControlFile.cache_sender_data[assignment_name]
        else:
            return None
