import json
import logging
import os

from tornado.httpclient import AsyncHTTPClient

from typing import Dict

import requests


# course setup service name
INTENAL_SERVICE_NAME = os.environ.get('DOCKER_SETUP_COURSE_SERVICE_NAME') or 'setup-course'
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


async def register_new_service(data: Dict[str, str]) -> str:
    """
    Helps to register (asynchronously) new course definition through the setup-course service
    Args:
        data: a dict with the org, course_id (label) and the domain.

    Example:
    ```await SetupCourseService.register_new_service(data = {
            'org': org,
            'course_id': course_id,
            'domain': handler.request.host,
        })```
    
    Returns: the response as json

    """
    client = AsyncHTTPClient()

    response = await client.fetch(
        SERVICE_BASE_URL, headers=SERVICE_COMMON_HEADERS, body=json.dumps(data), method='POST',
    )
    if not response.body:
        raise json.JSONDecodeError('The setup course response body is empty', '', 0)
    resp_json = json.loads(response.body)
    logger.debug(f'Setup-Course service response: {resp_json}')
    return resp_json


def make_rolling_update() -> None:
    """
    Triggers the rolling-update request BUT without wait for the response.
    It's very important to understand that we not have to wait 'cause the current process/jupyterhub will be killed
    """
    client = AsyncHTTPClient()
    url = f'{SERVICE_BASE_URL}/rolling-update'
    # WE'RE NOT USING <<<AWAIT>>> because the rolling update should occur later
    client.fetch(url, headers=SERVICE_COMMON_HEADERS, body='', method='POST')
