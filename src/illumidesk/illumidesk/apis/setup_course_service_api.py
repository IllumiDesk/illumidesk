import os

from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPError
from tornado.httpclient import HTTPResponse  # noqa: F401

from traitlets.config import LoggingConfigurable
from traitlets.traitlets import Bool

from typing import Any
from typing import Awaitable


class SetupCourseServiceAPI(LoggingConfigurable):
    """Class with helper functions to call the grader setup service RESTful API using a AsyncHTTPClient instance."""

    def __init__(self):
        self.client = AsyncHTTPClient()
        self.setup_course_service_name = os.environ.get('SETUP_COURSE_SERVICE_NAME') or 'grader-setup-service'
        self.setup_course_port = os.environ.get('SETUP_COURSE_PORT') or '8000'
        self.service_base_url = f'http://{self.setup_course_service_name}:{self.setup_course_port}'
        self.default_headers = {
            'Content-Type': 'application/json',
        }

    async def _request(self, endpoint: str, **kwargs: Any) -> Awaitable['HTTPResponse']:
        """
        Wrapper for the AsyncHTTPClient.fetch method which adds additional log outputs
        and headers.

        Args:
          endpoint: Grader Setup Service REST API endpoint

        Returns:
          HTTPResponse returned as a tornado.concurrent.Future object.
        """
        if not endpoint:
            raise ValueError('missing endpoint argument')
        headers = kwargs.pop('headers', {})
        headers.update(self.default_headers)
        url = f'{self.service_base_url}/{endpoint}'
        self.log.debug(f'Creating request with url: {url}')
        return await self.client.fetch(url, headers=headers, **kwargs)

    async def create_assignment_source_dir(self, org_name: str, course_id: str, assignment_name: str) -> Bool:
        """
        Calls the grader setup service to create the assignment source directory

        Args:
          org_name: the organization name
          course_id: the course name or course identifier
          assignment_name: the assignment name

        Returns:
          True when the service response is 200
        """
        try:
            response = await self._request(
                f'{self.service_base_url}/courses/{org_name}/{course_id}/{assignment_name}',
                headers=self.default_headers,
                body='',
                method='POST',
            )
            self.log.debug(f'Grader-setup service response: {response.body}')
            return True
        except HTTPError as e:
            # HTTPError is raised for non-200 responses
            self.log.error(f'Grader-setup service returned an error: {e}')

        return False

    async def register_new_service(self, org_name: str, course_id: str) -> Bool:
        """
        Helps to register (asynchronously) new course definition through the grader setup service

        Args:
          org_name: organization name
          course_id: the course name detected in the request args

        Returns:
          True when a new deployment was launched (k8s) otherwise False
        """
        try:
            response = await self._request(
                f'{self.service_base_url}/services/{org_name}/{course_id}',
                headers=self.default_headers,
                body='',
                method='POST',
            )
            self.log.debug(f'Grader-setup service response: {response.body}')
            return True
        except HTTPError as e:
            # HTTPError is raised for non-200 responses
            # the response can be found in e.response.
            self.log.error(f'Grader-setup service returned an error: {e}')

        return False

    async def register_control_file(
        self,
        assignment_name: str,
        lis_outcome_service_url: str,
        lis_result_sourcedid: str,
        lms_user_id: str,
        course_id: str,
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

        Returns:
          True when a new the control file was created and saved, false otherwise

        """
        try:
            response = await self._request(
                f'{self.service_base_url}/control-file/{assignment_name}/{lis_outcome_service_url}/{lis_result_sourcedid}/{lms_user_id}/{course_id}',
                headers=self.default_headers,
                body='',
                method='POST',
            )
            self.log.debug(f'Grader-setup service response: {response.body}')
            return True
        except HTTPError as e:
            # HTTPError is raised for non-200 responses
            # the response can be found in e.response.
            self.log.error(f'Grader-setup service returned an error: {e}')

        return False
