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


def get_current_service_definitions() -> str:
    """
    Gets the file content that contains the new services and groups that are used as grader services

    Returns: the contents of configuration file
    """
    # get the response from service config endpoint
    response = requests.get(f'{SERVICE_BASE_URL}/config')
    # store course setup configuration
    config = response.json()
    return config


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


def make_rolling_update() -> None:
    """
    Triggers the rolling-update request BUT without wait for the response.
    It's very important to understand that we not have to wait 'cause the current process/jupyterhub will be killed
    """
    client = AsyncHTTPClient()
    url = f'{SERVICE_BASE_URL}/rolling-update'
    # WE'RE NOT USING <<<AWAIT>>> because the rolling update should occur later
    client.fetch(url, headers=SERVICE_COMMON_HEADERS, body='', method='POST')
