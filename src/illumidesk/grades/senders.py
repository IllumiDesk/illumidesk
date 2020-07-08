from datetime import datetime
import json
import logging
import time
import os

from datetime import datetime

from lti.outcome_request import OutcomeRequest

from pathlib import Path

from nbgrader.api import Gradebook, MissingEntry

from tornado.httpclient import AsyncHTTPClient

from illumidesk.lti13.auth import get_lms_access_token

from illumidesk.lti13.auth import get_lms_access_token

from .exceptions import GradesSenderCriticalError
from .exceptions import AssignmentWithoutGradesError
from .exceptions import GradesSenderMissingInfoError

from .sender_controlfile import LTIGradesSenderControlFile


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
        """
        Creates a new class to help us to send grades saved in the nbgrader gradebook (sqlite) back to the LMS

        Args:
            course_id: It's the course label obtained from lti claims
            assignment_name: the asignment name used on the nbgrader console
            auth_state: It's a dictionary with the auth state of the user. Saved when user logged in.
                        The required key is 'course_lineitems' (obtained from the https://purl.imsglobal.org/spec/lti-ags/claim/endpoint claim)
                        and its value is something like 'http://canvas.instructure.com/api/lti/courses/1/line_items'
        """
        super(LTI13GradeSender, self).__init__(course_id, assignment_name)
        if auth_state is None or 'course_lineitems' not in auth_state:
            logger.info('The key "course_lineitems" is missing in the user auth_state and it is required')
            raise GradesSenderMissingInfoError()

        logger.info(f'User auth_state received from SenderHandler: {auth_state}')
        self.lineitems_url = auth_state['course_lineitems']
        self.private_key_path = os.environ.get('LTI13_PRIVATE_KEY')
        self.lms_token_url = os.environ['LTI13_TOKEN_URL']
        self.lms_client_id = os.environ['LTI13_CLIENT_ID']

    async def _get_line_item_info_by_assignment_name(self) -> str:
        client = AsyncHTTPClient()
        resp = await client.fetch(self.lineitems_url, headers=self.headers)
        items = json.loads(resp.body)
        logger.debug(f'LineItems got from {self.lineitems_url} -> {items}')
        if not items or isinstance(items, list) is False:
            raise GradesSenderMissingInfoError(f'No line-items were detected for this course: {self.course_id}')
        lineitem_matched = None
        for item in items:
            if self.assignment_name.lower() == item['label'].lower():
                lineitem_matched = item['id']  # the id is the full url
                logger.debug(f'There is a lineitem matched with the assignment {self.assignment_name}. {item}')
                break
        if lineitem_matched is None:
            raise GradesSenderMissingInfoError(f'No lineitem matched with the assignment name: {self.assignment_name}')

        resp = await client.fetch(lineitem_matched, headers=self.headers)
        lineitem_info = json.loads(resp.body)
        logger.debug(f'Fetched lineitem info from lms {lineitem_info}')

        return lineitem_info

    async def _set_access_token_header(self):
        token = await get_lms_access_token(self.lms_token_url, self.private_key_path, self.lms_client_id)

        if 'access_token' not in token:
            logger.info(f'response from {self.lms_token_url}: {token}')
            raise GradesSenderCriticalError('The "access_token" key is missing')

        # set all the headers to use in lms requests
        self.headers = {
            'Authorization': '{token_type} {access_token}'.format(**token),
            'Content-Type': 'application/vnd.ims.lis.v2.lineitem+json',
        }

    async def send_grades(self):
        max_score, nbgrader_grades = self._retrieve_grades_from_db()
        if not nbgrader_grades:
            raise AssignmentWithoutGradesError

        await self._set_access_token_header()

        lineitem_info = await self._get_line_item_info_by_assignment_name()
        score_maximum = lineitem_info['scoreMaximum']
        client = AsyncHTTPClient()
        self.headers.update({'Content-Type': 'application/vnd.ims.lis.v1.score+json'})
        for grade in nbgrader_grades:
            score = float(grade['score'])
            data = {
                'timestamp': datetime.now().isoformat(),
                'userId': grade['lms_user_id'],
                'scoreGiven': score,
                'scoreMaximum': score_maximum,
                'gradingProgress': 'FullyGraded',
                'activityProgress': 'Completed',
                'comment': '',
            }
            logger.info(f'data used to sent scores: {data}')

            url = lineitem_info['id'] + '/scores'
            logger.debug(f'URL for lineitem grades submission {url}')
            await client.fetch(url, body=json.dumps(data), method='POST', headers=self.headers)
