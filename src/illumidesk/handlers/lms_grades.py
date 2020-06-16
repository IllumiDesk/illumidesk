import json
import logging
import os
from pathlib import Path
import time

from filelock import FileLock

from jupyterhub.handlers import BaseHandler

from nbgrader.api import Gradebook
from nbgrader.api import MissingEntry

from tornado.web import HTTPError

from lti.outcome_request import OutcomeRequest


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GradesSenderError(Exception):
    """
    Base class for submission errors
    """

    pass


class GradesSenderCriticalError(GradesSenderError):
    """
    Error to identify when something critical happened
    In this case, the problem will continue until an admin checks the logs
    """

    pass


class AssignmentWithoutGradesError(GradesSenderError):
    """
    Error to identify when a submission request was made but there are not yet grades in the gradebook.db
    """

    pass


class GradesSenderMissingInfoError(GradesSenderError):
    """
    Error to identify when a assignment is not related or associated correctly between lms and nbgrader
    """

    pass


class SendGradesHandler(BaseHandler):
    """
    Defines a POST method to process grades submission for a specific assignment within a course
    """

    async def post(self, course_id: str, assignment_name: str) -> None:
        """
        Receives a request with the course name and the assignment name as path parameters
        which then uses the LTIGradeSender.send_grades function to extract data from the
        grader's database and sends it to the tool consumer / platform.
        
        Arguments:
          course_id: course name which has been previously normalized by the LTIUtils.normalize_name_for_containers
            function.
          assignment_name: assignment name which should coincide with the assignment name within the LMS.
          
        Raises:
          GradesSenderCriticalError if there was a critical error when either extracting grades from the db
            or sending grades to the tool consumer / platform.
          AssignmentWithoutGradesError if the assignment does not have any grades associated to it.
          GradesSenderMissingInfoError if ther is missing information when attempting to send grades.
        """
        self.log.debug(f'Data received to send grades-> course:{course_id}, assignment:{assignment_name}')

        lti_grade_sender = LTIGradeSender(course_id, assignment_name)
        try:
            lti_grade_sender.send_grades()
        except GradesSenderCriticalError:
            raise HTTPError(400, 'There was an critical error, please check logs.')
        except AssignmentWithoutGradesError:
            raise HTTPError(400, 'There are no grades yet to submit')
        except GradesSenderMissingInfoError:
            raise HTTPError(400, 'Unable to send grades. There are missing values, please check logs.')
        self.write(json.dumps({'success': True}))


class LTIGradesSenderControlFile:
    """
    Control file to register assignment information about grades submission.
    With this file we can associate assignments that come from lms and those that teachers create on nbgrader

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
        """Property which returns the configuration file full path name"""
        return os.path.join(self.config_path, LTIGradesSenderControlFile.FILE_NAME)

    def initialize_control_file(self) -> None:
        """
        Initializes the json control file by opening a file using the config_fullname property
        """
        with FileLock(LTIGradesSenderControlFile.lock_file):
            with Path(self.config_fullname).open('w+') as new_file:
                json.dump(LTIGradesSenderControlFile.cache_sender_data, new_file)
                logger.debug('Control file initialized.')

    def _loadFromFile(self) -> None:
        """
        Loads the send grades configuration by opening and examing the opened file. A new config
        file is created if the file doesn't exist or if it has the wrong format, a new one is created.
        Once opened, the file contents are cached.

        Once opened, the FILE_LOADED flag is set to True.

        Raises:
          JSONDecodeError the file could not be loaded.
        """
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
        Registers some information about where sent the assignment grades: like the url, sourcedid.
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
            assignment_points:
                This value is used to calculate the score before sending grades to lms.
                For canvas, is obtained from 'custom_canvas_assignment_points_possible'
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
        """
        Writes the assignment information to the configuration file.

        Args:
          assignment_name: the valid assignment name
          data: data that contains the information to identify the assignment within the LMS
        """
        # append new info
        LTIGradesSenderControlFile.cache_sender_data[assignment_name] = data
        # save the file to disk
        with Path(self.config_fullname).open('r+') as file:
            json.dump(LTIGradesSenderControlFile.cache_sender_data, file)

    def get_assignment_by_name(self, assignment_name: str) -> None:
        """
        Gets the assignment by assignment name. The assignment name is the assignment name
        within the gradbook's database.

        Args:
          assignment_name: the assignment name
        """
        if assignment_name in LTIGradesSenderControlFile.cache_sender_data:
            return LTIGradesSenderControlFile.cache_sender_data[assignment_name]
        else:
            return None


class LTIGradeSender:
    """
    This class helps to send student grades from nbgrader database.

    Args:
        course_id (str): Course id or name used in nbgrader
        assignment_name (str): Assignment name that needs to be processed and from which the grades are retrieved
    """

    def __init__(self, course_id: str, assignment_name: str):
        self.course_id = course_id
        self.assignment_name = assignment_name

    def _message_identifier(self):
        """Internal method to help keep track of when grades are sent to the LMS"""
        return '{:.0f}'.format(time.time())

    @property
    def grader_name(self):
        """Property that returns the shared grader's name. For example, i the course is named
        intro101 then the grader_name is `grader-intro101`."""
        return f'grader-{self.course_id}'

    @property
    def gradebook_dir(self):
        """Property that returns the full course path location wihin the shared grader's home directory"""
        return f'/home/{self.grader_name}/{self.course_id}'

    def _retrieve_grades_from_db(self):
        """
        Retrievs grades from the share grader account database.

        Raises:
          GradesSenderCriticalError if the gradebook does not exist or cannot be opened.
          MissingEntry if there are missing assignments from the database.
        """
        db_url = Path(self.gradebook_dir, 'gradebook.db')
        # raise an error if the database does not exist
        if not db_url.exists():
            logger.error(f'Gradebook database file does not exist at: {db_url}.')
            raise GradesSenderCriticalError

        out = []
        max_score = 0
        # Create the connection to the gradebook database
        with Gradebook(f'sqlite:///{db_url}', course_id=self.course_id) as gb:
            try:
                # retrieve the assignment record
                assignment_row = gb.find_assignment(self.assignment_name)
                max_score = assignment_row.max_score
                submissions = gb.assignment_submissions(self.assignment_name)
                logger.info(f'Found {len(submissions)} submissions for assignment: {self.assignment_name}')
            except MissingEntry as e:
                logger.info('Assignment or Submission is missing in database: %s' % e)
                raise GradesSenderMissingInfoError

            for submission in submissions:
                # retrieve the student to use the lms id
                student = gb.find_student(submission.student_id)
                out.append({'score': submission.score, 'lms_user_id': student.lms_user_id})
        logger.info(f'Grades found: {out}')
        logger.info('max_score for this assignment %s' % max_score)
        return max_score, out

    def send_grades(self) -> None:
        """
        Sends grades to the LMS.

        Raises:
          AssignmentWithoutGradesError if the assignment has not been graded.
          GradesSenderMissingInfoError if the config file doesn't have the information to send the result/score
            to the LMS.
        """
        max_score, nbgrader_grades = self._retrieve_grades_from_db()
        if not nbgrader_grades:
            raise AssignmentWithoutGradesError
        msg_id = self._message_identifier()
        # create the consumers map {'consumer_key': {'secret': 'shared_secret'}}
        consumer_key = os.environ.get('LTI_CONSUMER_KEY')
        shared_secret = os.environ.get('LTI_SHARED_SECRET')
        # get assignment info from control file
        grades_sender_file = LTIGradesSenderControlFile(self.gradebook_dir)
        assignment_info = grades_sender_file.get_assignment_by_name(self.assignment_name)
        if not assignment_info:
            logger.warning(
                f'There is no info related to assignment: {self.assignment_name}. Check if the config file path is correct'
            )
            raise GradesSenderMissingInfoError

        url = assignment_info['lis_outcome_service_url']
        # for each grade in nbgrader db, use the info saved in control file to process each student submission
        for grade in nbgrader_grades:
            # get student lis_result_sourcedid
            logger.info(f"Retrieving info for student id:{grade['lms_user_id']}")
            student_array = [s for s in assignment_info['students'] if s['lms_user_id'] == grade['lms_user_id']][:1]
            # student object is an array []
            if student_array:
                student = student_array[0]
                logger.info(f'Student data retrieved sender control file: {student}')
                # detect if sourcedid contains backslash to escape quotes
                if '\"' in student['lis_result_sourcedid']:
                    student['lis_result_sourcedid'] = student['lis_result_sourcedid'].replace('\"', '"')

                score = float(grade['score'])
                # calculate the percentage
                max_score = float(max_score)
                score = score * 100 / max_score / 100
                outcome_args = {
                    'lis_outcome_service_url': url,
                    'lis_result_sourcedid': student['lis_result_sourcedid'],
                    'consumer_key': consumer_key,
                    'consumer_secret': shared_secret,
                }
                req = OutcomeRequest(outcome_args)
                # send to lms through lti package (we used pylti before but some errors found with moodle)
                outcome_result = req.post_replace_result(score)
                if outcome_result.is_success():
                    logger.info('Your score was submitted. Great job!')
                else:
                    logger.error('An error occurred while saving your score. Please try again.')
                    raise GradesSenderCriticalError
