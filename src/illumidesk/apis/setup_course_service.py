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


class SetupCourseService:
    """
    Wrapper class that contains the logic to make requests to our internal setup-course service
    """

    base_url = f'http://{INTENAL_SERVICE_NAME}:{SERVICE_PORT}'
    common_headers = {'Content-Type': 'application/json'}

    @staticmethod
    def get_current_service_definitions() -> str:
        """
        Gets the file content that contains the new services and groups that are used as grader services
        """
        # get the response from service config endpoint
        response = requests.get(f'{SetupCourseService.base_url}/config')
        # store course setup configuration
        config = response.json()
        return config

    @staticmethod
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

        """
        client = AsyncHTTPClient()

        response = await client.fetch(
            SetupCourseService.base_url,
            headers=SetupCourseService.common_headers,
            body=json.dumps(data),
            method='POST',
        )
        if not response.body:
            raise json.JSONDecodeError('The setup course response body is empty', '', 0)
        resp_json = json.loads(response.body)
        logger.debug(f'Setup-Course service response: {resp_json}')
        return resp_json

    @staticmethod
    def make_rolling_update() -> None:
        """
        Triggers the rolling-update request BUT without wait for the response.
        It's very important to understand that we not have to wait 'cause the current process/jupyterhub will be killed
        """
        client = AsyncHTTPClient()
        url = f'{SetupCourseService.base_url}/rolling-update'
        # WE'RE NOT USING <<<AWAIT>>> because the rolling update should occur later
        client.fetch(url, headers=SetupCourseService.common_headers, body='', method='POST')
