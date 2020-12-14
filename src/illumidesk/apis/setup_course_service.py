import logging
import os

from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPError

import requests
from traitlets.traitlets import Bool


# course setup service name
INTENAL_SERVICE_NAME = os.environ.get('DOCKER_SETUP_COURSE_SERVICE_NAME') or 'grader-setup-service'
# course setup service port
SERVICE_PORT = os.environ.get('DOCKER_SETUP_COURSE_PORT') or '8000'


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


SERVICE_BASE_URL = f'http://{INTENAL_SERVICE_NAME}:{SERVICE_PORT}'
SERVICE_COMMON_HEADERS = {'Content-Type': 'application/json'}


async def create_assignment_source_dir(org_name: str, course_id: str, assignment_name: str) -> Bool:
    """
    Calls the grader setup service to create the assignment source directory

    returns: True when the service response is 200
    """
    client = AsyncHTTPClient()
    try:
        response = await client.fetch(
            f'{SERVICE_BASE_URL}/courses/{org_name}/{course_id}/{assignment_name}',
            headers=SERVICE_COMMON_HEADERS,
            body='',
            method='POST',
        )
        logger.debug(f'Grader-setup service response: {response.body}')
        return True
    except HTTPError as e:
        # HTTPError is raised for non-200 responses
        logger.error(f'Grader-setup service returned an error: {e}')
        return False


async def register_new_service(org_name: str, course_id: str) -> Bool:
    """
    Helps to register (asynchronously) new course definition through the setup-course service
    Args:
        org: organization name
        course_id: the course name detected in the request args
    Returns: True when a new deployment was launched (k8s) otherwise False

    """
    client = AsyncHTTPClient()
    try:
        response = await client.fetch(
            f'{SERVICE_BASE_URL}/services/{org_name}/{course_id}',
            headers=SERVICE_COMMON_HEADERS,
            body='',
            method='POST',
        )
        logger.debug(f'Grader-setup service response: {response.body}')
        return True
    except HTTPError as e:
        # HTTPError is raised for non-200 responses
        # the response can be found in e.response.
        logger.error(f'Grader-setup service returned an error: {e}')
        return False
