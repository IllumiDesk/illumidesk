import json

import os

from tornado.httpclient import AsyncHTTPClient

from typing import Dict

import requests


# course setup service name
INTENAL_SERVICE_NAME = os.environ.get('DOCKER_SETUP_COURSE_SERVICE_NAME') or 'setup-course'
# course setup service port
SERVICE_PORT = os.environ.get('DOCKER_SETUP_COURSE_PORT') or '8000'


class SetupCourseService:
    """
    Wrapper class that contains the logic to make requests to our internal setup-course service
    """
    @staticmethod
    def get_current_service_definitions() -> str:
        """
        Gets the file content that contains the new services and groups that are used as grader services
        """
        # get the response from service config endpoint
        response = requests.get(f'http://{INTENAL_SERVICE_NAME}:{SERVICE_PORT}/config')
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
        url = f'http://{INTENAL_SERVICE_NAME}:{SERVICE_PORT}'
        headers = {'Content-Type': 'application/json'}
        response = await client.fetch(url, headers=headers, body=json.dumps(data), method='POST')
        if not response.body:
            raise json.JSONDecodeError('The setup course response body is empty', '', 0)
        resp_json = json.loads(response.body)
        return resp_json