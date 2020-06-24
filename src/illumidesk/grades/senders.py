import datetime
import json
import logging
import pem
import time
import os

from filelock import FileLock
from illumidesk.lti13.auth import get_lms_access_token
from pathlib import Path

from lti.outcome_request import OutcomeRequest
from nbgrader.api import Gradebook, MissingEntry
from tornado.httpclient import AsyncHTTPClient
from urllib.parse import urlsplit

from .exceptions import (
    GradesSenderCriticalError,
    AssignmentWithoutGradesError,
    GradesSenderMissingInfoError,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class GradesBaseSender:
    """
    This class helps to send student grades from nbgrader database.

    Args:
        course_id (str): Course id or name used in nbgrader
        assignment_name (str): Assignment name that needs to be processed and from which the grades are retrieved
    """
    def __init__(self, course_id: str, assignment_name: str):
        self.course_id = course_id
        self.assignment_name = assignment_name

    async def send_grades(self):
        raise NotImplementedError()

    @property
    def grader_name(self):
        return f'grader-{self.course_id}'

    @property
    def gradebook_dir(self):
        return f'/home/{self.grader_name}/{self.course_id}'

    def _retrieve_grades_from_db(self):
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


class LTIGradeSender(GradesBaseSender):
    """
    This class implements the grades submission for LTI 1.1
    """

    def _message_identifier(self):
        return '{:.0f}'.format(time.time())

    async def send_grades(self) -> None:
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
                f'There is not info related to assignment: {self.assignment_name}. Check if the config file path is correct'
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

class LTI13GradeSender(GradesBaseSender):

    def __init__(self, course_id: str, assignment_name: str, auth_state: dict):
        super(LTI13GradeSender, self).__init__(course_id, assignment_name)
        # lti 13 endpoint contains the jwks url so we need to extract only the hostname
        lms_jwks_endpoint = os.environ['LTI13_ENDPOINT']
        self.user_auth_state = auth_state
        logger.info(f'User auth_state received from SenderHandler: {self.user_auth_state}')
        self.lineitems_url = self.user_auth_state['course_lineitems']
        if not self.lineitems_url:
            logger.info('There is not lineitems value for grades submission')
            raise GradesSenderMissingInfoError()
        self.lms_base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(lms_jwks_endpoint))        
        logger.info(f'Using {self.lineitems_url} to get line_items from lms')

    async def get_lms_token(self):
        key_path = os.environ.get('LTI13_PRIVATE_KEY')
        # check the pem permission
        if not os.access(key_path, os.R_OK):
            logger.error(f'The pem file {key_path} cannot be load')
            raise PermissionError()
        # parse file generates a list of PEM objects
        certs = pem.parse_file(key_path)
        self.token = await get_lms_access_token(            
            os.environ['LTI13_TOKEN_URL'],
            str(certs[0]),
            os.environ['LTI13_CLIENT_ID'],
        )

    async def send_grades(self):
        await self.get_lms_token()
        max_score, nbgrader_grades = self._retrieve_grades_from_db()
        if not nbgrader_grades:
            raise AssignmentWithoutGradesError

        for grade in nbgrader_grades:
            headers = {
            'Authorization': '{token_type} {access_token}'.format(**self.token),
            'Content-Type': 'application/vnd.ims.lis.v2.lineitem+json'
            }
            client = AsyncHTTPClient()
            resp = await client.fetch(self.lineitems_url, headers=headers)
            items = json.loads(resp.body)
            logger.debug(f'LineItems got from {self.lineitems_url} -> {items}')
            lineitem = None
            for item in items:
                if self.assignment_name.lower() == item['label'].lower():
                    lineitem = item['id']
                    logger.debug(f'There is a lineitem matched with the assignment {self.assignment_name}. {item}')
                    break
            if lineitem is None:
                return
            resp = await client.fetch(lineitem, headers=headers)
            line_item = json.loads(resp.body)
            logger.debug('Fetched lineitem info from lms %s' % line_item)
            score = float(grade['score'])
            # calculate the percentage
            max_score = float(max_score)
            score = score * 100 / max_score / 100
            data = {
                'timestamp': datetime.now().isoformat(),
                'userId': grade['lms_user_id'],
                'scoreGiven': score,
                'scoreMaximum': line_item['scoreMaximum'],
                'gradingProgress': 'FullyGraded',
                'activityProgress': 'Completed',
                'comment': '',
            }
            logger.info('data used to sent scores:', data)
            headers.update({'Content-Type': 'application/vnd.ims.lis.v1.score+json'})
            url = lineitem + '/scores'
            logger.debug('URL for lineitem grades submission %s' % url)
            await client.fetch(url, body=json.dumps(data), method='POST', headers=headers)