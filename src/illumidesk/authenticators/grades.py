import os
import json
import logging

from datetime import datetime

from importlib import import_module

from tornado.httpclient import AsyncHTTPClient

from traitlets.config import LoggingConfigurable

from .lms import get_lms_access_token


logger = logging.getLogger(__name__)


class GradesSender(LoggingConfigurable):
    """
    Base for sending grades to the LMS.
    """

    def __init__(self, course_id, assignment_name, grades, url):
        self.url = url
        self.course_id = course_id
        self.assignment_name = assignment_name
        self.grades = grades

    def send(self):
        raise NotImplementedError()


class CanvasSender(GradesSender):
    """
    Povides functionality to send grades to the Canvas LMS
    """

    async def _send_grades(self, assignment_name, token, grade, user_id, lineitems, lms):
        """
        Sends grades to the LMS with LTI 1.3.

        Args:
            assignment_name: the assignment name
            token: the token used to authenticate to the LMS
            grade: the grade to post for the assignment
            user_id: the user's unique user_id
            lineitems: lineitems to send grades
            lms: the LMS url endpoint to send grades

        Returns:
            Response from send grades endpoint
        """
        if not assignment_name:
            raise ValueError('assignment_name missing')
        if not token:
            raise ValueError('token missing')
        if not grade:
            raise ValueError('grade missing')
        if not user_id:
            raise ValueError('user_id missing')
        if not lineitems:
            raise ValueError('lineitems missing')
        if not lms:
            raise ValueError('lms missing')
        headers = {
            'Authorization': '{token_type} {access_token}'.format(**token),
            'Content-Type': 'application/vnd.ims.lis.v2.lineitem+json',
        }
        client = AsyncHTTPClient()
        resp = await client.fetch(lineitems, headers=headers)
        items = json.loads(resp.body)
        logger.debug('Sending grades %s' % items)
        lineitem = None
        for item in items:
            if assignment_name.lower() == item['label'].lower():
                lineitem = item['id']
                logger.debug('Obtained lineitem %s' % item)
        if lineitem is None:
            return
        resp = await client.fetch(lineitem, headers=headers)
        line_item = json.loads(resp.body)
        logger.debug('Fetched lineitem %s' % line_item)
        data = {
            'timestamp': datetime.now().isoformat(),
            'userId': user_id,
            'scoreGiven': grade,
            'scoreMaximum': line_item['scoreMaximum'],
            'gradingProgress': 'FullyGraded',
            'activityProgress': 'Completed',
            'comment': '',
        }
        logger.info('Seding grades with data %s' % data)
        headers.update({'Content-Type': 'application/vnd.ims.lis.v1.score+json'})
        url = lineitem + '/scores'
        logger.debug('URL for lineitem %s' % url)
        await client.fetch(url, body=json.dumps(data), method='POST', headers=headers)

    async def send(self):
        """
        Gets all the necessary variables to then call the internal _send_grades
        method which sends the grades (scores) to the LMS.
        """
        token = await get_lms_access_token(
            self.url, os.environ['LMS_TOKEN_ENDPOINT'], os.environ['PRIVATE_KEY'], os.environ['LMS_CLIENT_ID'],
        )
        self.log.debug('Sending grades with token %s' % token)
        lms_endpoint = os.environ['LMS_ENDPOINT']
        self.log.debug('Sending grades with lms_endpoint %s' % lms_endpoint)
        lineitems = f'{lms_endpoint}/api/lti/courses/{self.course_id}/line_items'
        self.log.debug('Sending grades with URL %s' % lineitems)
        for grades in self.grades:
            await self._send_grades(
                self.assignment_name, token, grades['grade'], grades['user_id'], lineitems, self.url
            )


def get_sender(course_id, assignment_name, data, url):
    path = os.environ.get('GRADES_SENDER', 'auth.grades.CanvasSender')
    module_path, class_name = path.rsplit('.', 1)
    module = import_module(module_path)
    sender_cls = getattr(module, class_name)
    return sender_cls(course_id, assignment_name, data, url)
