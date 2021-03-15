import logging
import os

from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPError

from traitlets.traitlets import Bool


# course setup service name
INTENAL_SERVICE_NAME = os.environ.get('SETUP_COURSE_SERVICE_NAME') or 'grader-setup-service'
# course setup service port
SERVICE_PORT = os.environ.get('SETUP_COURSE_PORT') or '8000'


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


async def register_new_service(org_name: str, course_id: str) -> bool:
    """
    Helps to register (asynchronously) new course definition through the grader setup service
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


async def register_control_file(
    assignment_name: str, lis_outcome_service_url: str, lis_result_sourcedid: str, lms_user_id: str, course_id: str
) -> bool:
    """
    Helps to register the control file to keep track of assignments and resource id's with the LMS to
    send grades.

    Args:
        assignment_name: string representation of the assignment name from the LMS (normalized)
        lis_outcome_service_url: url endpoint that is used to send grades to the LMS with LTI 1.1
        lis_result_sourcedid: unique assignment or module identifier used with LTI 1.1
        lms_user_id: unique (opaque) user id
        course_id: the course id within the lms

    Returns: True when a new the control file was created and saved, false otherwise

    """

    client = AsyncHTTPClient()
    try:
        response = await client.fetch(
            f'{SERVICE_BASE_URL}/control-file/{assignment_name}/{lis_outcome_service_url}/{lis_result_sourcedid}/{lms_user_id}/{course_id}',
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
