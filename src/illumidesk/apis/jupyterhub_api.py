import json
import os

from nbgrader.api import Gradebook
from nbgrader.api import InvalidEntry

from pathlib import Path

from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClientError
from tornado.httpclient import HTTPResponse  # noqa: F401

from traitlets.config import LoggingConfigurable

from typing import Any
from typing import Awaitable


class JupyterHubAPI(LoggingConfigurable):
    """
    Class used to communicate with JupyterHub using the REST API.

    Attributes:
      client: an instance of tornado's AsyncHTTPClient
      token: valid JupyterHub API token
      api_root_url: JupyterHUb's API url endpoint
      default_headers: default request headers
    """

    def __init__(self):
        self.client = AsyncHTTPClient()
        self.token = os.environ.get('JUPYTERHUB_API_TOKEN')
        if not self.token:
            raise EnvironmentError('JUPYTERHUB_API_TOKEN env-var is not set')
        self.api_root_url = os.environ.get('JUPYTERHUB_API_URL')
        if not self.api_root_url:
            raise EnvironmentError('JUPYTERHUB_API_URL env-var is not set')
        self.default_headers = {
            'Authorization': f'token {self.token}',
            'Content-Type': 'application/json',
        }

    async def _request(self, endpoint: str, **kwargs: Any) -> Awaitable['HTTPResponse']:
        """
        Wrapper for the AsyncHTTPClient.fetch method which adds additional log outputs
        and headers.

        Args:
          endpoint: JupyterHub REST API endpoint

        Returns:
          HTTPResponse returned as a tornado.concurrent.Future object.
        """
        if not endpoint:
            raise ValueError('missing endpoint argument')
        headers = kwargs.pop('headers', {})
        headers.update(self.default_headers)
        url = f'{self.api_root_url}/{endpoint}'
        self.log.debug(f'Creating request with url: {url}')
        return await self.client.fetch(url, headers=headers, **kwargs)

    async def create_group(self, group_name: str) -> Awaitable['HTTPResponse']:
        """
        Creates a group.

        Args:
          group_name: the group name to create

        Returns:
          Response from the endpoint
        """
        if not group_name:
            raise ValueError('group_name missing')
        self.log.debug(f'Creating group with path groups/{group_name}')
        try:
            return await self._request(f'groups/{group_name}', body='', method='POST')
        except HTTPClientError as e:
            if e.code != 409:
                self.log.info(f'Error creating student group {group_name} with exception {e}')
                return None
            return await self._request(f'groups/{group_name}')

    async def get_group(self, group_name: str) -> Awaitable['HTTPResponse']:
        """
        Gets a group

        Args:
          group_name: the group name to create

        Returns:
          Response from the endpoint
        """
        if not group_name:
            raise ValueError('group_name missing')
        self.log.debug(f'Getting group with path groups/{group_name}')
        return await self._request(f'groups/{group_name}')

    async def create_users(self, *users: str) -> Awaitable['HTTPResponse']:
        """
        Creates users from a list

        Args:
          users: a user list
        
        Returns:
          Response from the endpoint
        """
        if not users:
            raise ValueError('users missing')
        self.log.debug('Creating users body %s' % json.dumps({'usernames': users}))
        return await self._request('users', body=json.dumps({'usernames': users}), method='POST')

    async def create_user(self, username: str) -> Awaitable['HTTPResponse']:
        """
        Creates a user

        Args:
          username: the user's username to create
        
        Returns:
          Response from the endpoint
        """
        if not username:
            raise ValueError('username missing')
        self.log.debug(f'Creating user with path users/{username}')
        return await self._request(f'users/{username}', body='', method='POST')

    async def add_group_member(self, group_name: str, username: str) -> Awaitable['HTTPResponse']:
        """
        Adds a user to a group

        Args:
          group_name: the group name
          usernam: the user's unique name

        Returns:
          Response from the endpoint
        """
        if not group_name:
            raise ValueError('group_name missing')
        if not username:
            raise ValueError('username missing')
        self.log.debug(f'Adding user to group with path groups/{group_name}/users')
        self.log.debug('Adding user %s to group %s' % (json.dumps({'users': username}), group_name))
        return await self._request(
            f'groups/{group_name}/users', body=json.dumps({'users': [f'{username}']}), method='POST',
        )

    async def add_user_to_nbgrader_gradebook(
        self, course_id: str, username: str, lms_user_id: str
    ) -> Awaitable['HTTPResponse']:
        """
        Adds a user to the nbgrader gradebook database for the course.

        Args:
            course_id: The normalized string which represents the course label.
            username: The user's username
        Raises:
            InvalidEntry: when there was an error adding the user to the database
        """
        if not course_id:
            raise ValueError('course_id missing')
        if not username:
            raise ValueError('username missing')
        if not lms_user_id:
            raise ValueError('lms_user_id missing')
        grader_name = f'grader-{course_id}'
        db_url = Path('/home', grader_name, course_id, 'gradebook.db')
        db_url.parent.mkdir(exist_ok=True, parents=True)
        self.log.debug('Database url path is %s' % db_url)
        if not db_url.exists():
            self.log.debug('Gradebook database file does not exist')
            return
        gradebook = Gradebook(f'sqlite:///{db_url}', course_id=course_id)
        try:
            gradebook.update_or_create_student(username, lms_user_id=lms_user_id)
            self.log.debug('Added user %s with lms_user_id %s to gradebook' % (username, lms_user_id))
        except InvalidEntry as e:
            self.log.debug('Error during adding student to gradebook: %s' % e)
        gradebook.close()

    async def add_student_to_jupyterhub_group(self, course_id: str, student: str) -> Awaitable['HTTPResponse']:
        """
        Adds a student to the student course group.

        Args:
            course_id: The normalized string which represents the course label.
            student: The student name
        Raises:
            HTTPClientError: when adding user to group
        """
        if not course_id:
            raise ValueError('course_id missing')
        if not student:
            raise ValueError('student missing')
        group_name = f'nbgrader-{course_id}'
        self.log.debug('Student group name is %s' % group_name)
        try:
            await self.create_group(group_name)
        except HTTPClientError as e:
            if e.code != 409:
                self.log.error('Error creating student group %s with exception %s' % (group_name, e))
        await self._add_user_to_jupyterhub_group(student, group_name)

    async def add_instructor_to_jupyterhub_group(self, course_id: str, instructor: str) -> Awaitable['HTTPResponse']:
        """
        Adds a an instructor to the student course group.

        Args:
            course_id: The normalized string which represents the course label.
            instructor: The instructor name
        Raises:
            HTTPClientError: when adding user to group
        """
        if not course_id:
            raise ValueError('course_id missing')
        if not instructor:
            raise ValueError('instructor missing')
        group_name = f'formgrade-{course_id}'
        self.log.debug('Instructor group name is %s' % group_name)
        try:
            await self.create_group(group_name)
        except HTTPClientError as e:
            if e.code != 409:
                self.log.error('Error creating instructors group')
        await self._add_user_to_jupyterhub_group(instructor, group_name)

    async def _add_user_to_jupyterhub_group(self, username: str, group_name: str) -> Awaitable['HTTPResponse']:
        """
        Adds a user to a JupyterHub group.

        Args:
            usernames: The user's name
            group_name: The group's name
        Raises:
            HTTPClientError: when adding user to group
        """
        if not username:
            raise ValueError('username missing')
        if not group_name:
            raise ValueError('group_name missing')
        try:
            self.log.debug('Creating %s' % (username))
            await self.create_user(username)
        except HTTPClientError as http_error:
            if http_error.code != 409:
                self.log.debug('Error adding %s' % username)
        resp = await self.get_group(group_name)
        self.log.debug('Getting response %s' % resp.body)
        group_users = json.loads(resp.body)['users']
        self.log.debug('Group %s users are: %s' % (group_name, group_users))
        if username not in group_users:
            try:
                self.log.debug('Adding %s to group %s' % (username, group_name))
                await self.add_group_member(group_name, username)
            except HTTPClientError as http_error:
                if http_error.code != 409:
                    self.log.error('Error adding user to jupyterhub group %s' % http_error)
