import os
import json
import time
import logging
import sys
from pathlib import Path
from tornado import web
from xml.etree import ElementTree as etree
from jupyterhub.handlers import BaseHandler
from nbgrader.api import Gradebook
from nbgrader.api import MissingEntry
from pylti.common import LTIPostMessageException, post_message

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SendGradesHandler(BaseHandler):
    async def post(self, course_id, assignment_name):
        self.log.debug(f'course_id received: {course_id}')
        self.log.debug(f'assignment_name received: {assignment_name}')
        
        lti_grade_sender = LTIGradeSender(course_id, assignment_name)
        lti_grade_sender.send_grades()
        self.finish(json.dumps({'message': 'OK'}))


class LTIGradesSenderControlFile:
    # TODO: re-think to centralize files like this or replace all of them with a little DB (sqlite)
    # this file must be at same level of gradebook
    # the path is not calculated here but is like: /<mnt_root>/<org_name>/home/grader-<course-id>/<course-id>
    FILE_NAME = 'lti_grades_sender_info.json'
    cache_sender_data = {'grades_sender_assignments': []}

    def __init__(self, config_file_path):
        self.config_path = config_file_path
        if not LTIGradesSenderControlFile.sender_config:
            # try to read first time
            self.loadFromFile()

    @property
    def config_fullname(self):        
        return os.path.join(self.config_path, LTIGradesSenderControlFile.FILE_NAME)
    
    def loadFromFile(self):
        # TODO: apply a file lock         
        with Path(self.config_fullname).open('w+') as file:
            try:
                cache_sender_data = json.load(file)
            except json.JSONDecodeError:
                if Path(self.config_fullname).stat().st_size != 0:
                    raise
                else:
                    json.dump(cache_sender_data, file)
    
    def register_data(self, assignment_name, lis_outcome_service_url, lms_user_id, lis_result_sourcedid):
        assignment_reg = None
        # if the assignment does not exist then register it
        for item in self.sender_data['grades_sender_assignments']:
            if item['lms_name'] == assignment_name:
                assignment_reg = item
                break
        else:
            # it's a new assignment
            assignment_reg = {
                'lms_name': assignment_name,
                'lis_outcome_service_url': lis_outcome_service_url,
                'students': []
            }
        # if the student info not exists then create it
        if not [student for student in assignment_reg['students'] if student['lms_user_id'] == lms_user_id]:
            assignment_reg['students'].append({
                'lms_user_id': lms_user_id,
                'lis_result_sourcedid': lis_result_sourcedid
            })
            # only if a new assignment/student info was included save the file
            self._write_new_assignment_info(assignment_reg)

    def _write_new_assignment_info(self, data: dict):
        # append new info
        self.cache_sender_data['grades_sender_assignments'].append(data)
        # save the file to disk
        with Path(self.config_fullname).open('r+') as file:
            json.dump(self.cache_sender_data, file)

    def get_assignment_by_name(self, assignment_name):
        for item in self.sender_data['grades_sender_assignments']:
            if item['lms_name'] == assignment_name:
                return item


class LTIGradeSender:

    def __init__(self, log: any, course_id: str, assignment_name: str):
        self.course_id = course_id
        self.assignment_name = assignment_name
        self.log = log
        
    def _message_identifier(self):
        return '{:.0f}'.format(time.time())

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
            logger.error('Gradebook database file does not exist. impossible to send grades')
            return

        out = []
        # Create the connection to the gradebook database
        with Gradebook(f'sqlite:///{db_url}', course_id=course_id) as gb:        
            try:
                submissions = gb.assignment_submissions(assignment_name)
                logger.debug(f'Found {len(submissions)} submissions for assignment: {assignment_name}')
            except MissingEntry as e:
                logger.debug('Submission is missing: %s' % e)            
            
            for submission in submissions:
                # retrieve the student to use the lms id
                student = gb.find_student(submission.student_id)
                out.append({                    
                    'score': submission.score,
                    'lms_user_id': student.lms_user_id,
                })
        logger.debug(f'Grades found: {out}')
        return out

    def send_grades(self):
        nbgrader_grades = self._retrieve_grades_from_db()
        if not nbgrader_grades:
            logger.info('There are no grades yet to submit')
            return
        msg_id = self.message_identifier()
        # create the consumers map {'consumer_key': {'secret': 'shared_secret'}}
        consumer_key = os.environ.get('LTI_CONSUMER_KEY')
        shared_secret = os.environ.get('LTI_SHARED_SECRET')
        pylti_consumers = {}
        pylti_consumers[consumer_key] = {'secret': shared_secret}
        # get assignment info from control file
        grades_sender_file = LTIGradesSenderControlFile(self.gradebook_dir)
        assignment_info = grades_sender_file.get_assignment_by_name(self.assignment_name)
        if not assignment_info:
            logger.debug(f'There is not info related to assignment: {self.assignment_name}. Check if the config file path is correct')
            return
        
        url = assignment_info['lis_outcome_service_url']
        logger.debug(f'lis_outcome_service_url found to send grades:{url}')

        for grade in self.nbgrader_grades:
            # get student lis_result_sourcedid
            student = [s for s in assignment_info['students'] if s['lms_user_id'] == grade['lms_user_id']][:1]
            if student:
                score = float(grade['score'])
                # todo: if 0 <= score <= 1.0:
                lms_xml = generate_request_xml(msg_id, student['lis_result_sourcedid'], score)
                # send to lms


def generate_request_xml(message_identifier_id: str,
                         lis_result_sourcedid: str, score: float, operation = 'replaceResult'):
    # pylint: disable=too-many-locals
    """
    Generates LTI 1.1 XML for posting result to LTI consumer.
    :param message_identifier_id:
    :param operation:
    :param lis_result_sourcedid:
    :param score:
    :return: XML string
    """
    root = etree.Element(u'imsx_POXEnvelopeRequest',
                         xmlns=u'http://www.imsglobal.org/services/'
                               u'ltiv1p1/xsd/imsoms_v1p0')

    header = etree.SubElement(root, 'imsx_POXHeader')
    header_info = etree.SubElement(header, 'imsx_POXRequestHeaderInfo')
    version = etree.SubElement(header_info, 'imsx_version')
    version.text = 'V1.0'
    message_identifier = etree.SubElement(header_info,
                                          'imsx_messageIdentifier')
    message_identifier.text = message_identifier_id
    body = etree.SubElement(root, 'imsx_POXBody')
    xml_request = etree.SubElement(body, '%s%s' % (operation, 'Request'))
    record = etree.SubElement(xml_request, 'resultRecord')

    guid = etree.SubElement(record, 'sourcedGUID')

    sourcedid = etree.SubElement(guid, 'sourcedId')
    sourcedid.text = lis_result_sourcedid
    if score is not None:
        result = etree.SubElement(record, 'result')
        result_score = etree.SubElement(result, 'resultScore')
        language = etree.SubElement(result_score, 'language')
        language.text = 'en'
        text_string = etree.SubElement(result_score, 'textString')
        text_string.text = score.__str__()
    ret = "<?xml version='1.0' encoding='utf-8'?>\n{}".format(
        etree.tostring(root, encoding='utf-8').decode('utf-8'))

    return ret
