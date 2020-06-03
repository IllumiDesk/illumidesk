from json import JSONDecodeError
import os

from jupyterhub.auth import Authenticator

import pytest

from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient

from unittest.mock import patch

from illumidesk.apis.jupyterhub_api import JupyterHubAPI
from illumidesk.authenticators.authenticator import LTI11Authenticator
from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.authenticators.authenticator import setup_course_hook
from illumidesk.apis.jupyterhub_api import JupyterHubAPI

from tests.illumidesk.mocks import mock_handler
from tests.illumidesk.factory import factory_auth_state_dict
from tests.illumidesk.factory import factory_http_response


@pytest.mark.asyncio
async def test_setup_course_hook_is_assigned_to_lti11_authenticator_post_auth_hook():
    """
    Does the setup course hook get assigned to the post_auth_hook for the LTI11Authenticator?
    """
    authenticator = LTI11Authenticator(post_auth_hook=setup_course_hook)
    assert authenticator.post_auth_hook == setup_course_hook


@pytest.mark.asyncio
async def test_setup_course_hook_is_assigned_to_lti13_authenticator_post_auth_hook():
    """
    Does the setup course hook get assigned to the post_auth_hook for the LTI13Authenticator?
    """
    authenticator = LTI13Authenticator(post_auth_hook=setup_course_hook)
    assert authenticator.post_auth_hook == setup_course_hook


@pytest.mark.asyncio()
async def test_setup_course_hook_raises_environment_error_with_missing_org(monkeypatch, setup_course_hook_environ):
    """
    Is an environment error raised when the organization name is missing when calling
    the setup_course_hook function?
    """
    monkeypatch.setenv('ORGANIZATION_NAME', '')
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict()
    with pytest.raises(EnvironmentError):
        await local_authenticator.post_auth_hook(local_authenticator, local_handler, local_authentication)


@pytest.mark.asyncio()
async def test_setup_course_hook_raises_json_decode_error_without_client_fetch_response(
    monkeypatch, setup_course_environ, setup_course_hook_environ
):
    """
    Does the setup course hook raise a json decode error if the response form the setup course
    microservice is null or empty?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict()
    local_response = factory_http_response(handler=local_handler.request, body=None)

    with patch.object(
        JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
                with pytest.raises(JSONDecodeError):
                    await setup_course_hook(local_authenticator, local_handler, local_authentication)


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_student_to_jupyterhub_group_when_role_is_learner(
    setup_course_environ, setup_course_hook_environ
):
    """
    Is the jupyterhub_api add student to jupyterhub group function called when the user role is
    the learner role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict()
    local_response = factory_http_response(handler=local_handler.request)

    with patch.object(
        JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
                result = await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert mock_add_student_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_user_to_nbgrader_gradebook_when_role_is_learner(
    monkeypatch, setup_course_environ, setup_course_hook_environ
):
    """
    Is the jupyterhub_api add user to nbgrader gradebook function called when the user role is
    the learner role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict()
    local_response = factory_http_response(handler=local_handler.request)

    with patch.object(JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None):
        with patch.object(
            JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None
        ) as mock_add_user_to_nbgrader_gradebook:
            with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
                await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert mock_add_user_to_nbgrader_gradebook.called


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_instructor_to_jupyterhub_group_when_role_is_instructor(
    monkeypatch, setup_course_environ, setup_course_hook_environ
):
    """
    Is the jupyterhub_api add instructor to jupyterhub group function called when the user role is
    the instructor role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict(user_role='Instructor')
    local_response = factory_http_response(handler=local_handler.request)

    with patch.object(
        JupyterHubAPI, 'add_instructor_to_jupyterhub_group', return_value=None
    ) as mock_add_instructor_to_jupyterhub_group:
        with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
            await setup_course_hook(local_authenticator, local_handler, local_authentication)
            assert mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_does_not_call_add_student_to_jupyterhub_group_when_role_is_instructor(
    setup_course_environ, setup_course_hook_environ
):
    """
    Is the jupyterhub_api add student to jupyterhub group function called when the user role is
    the instructor role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict(user_role='Instructor')
    local_response = factory_http_response(handler=local_handler.request)

    with patch.object(
        JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(JupyterHubAPI, 'add_instructor_to_jupyterhub_group', return_value=None):
            with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
                await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert not mock_add_student_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_does_not_call_add_student_to_jupyterhub_group_when_role_is_instructor(
    setup_course_environ, setup_course_hook_environ
):
    """
    Is the jupyterhub_api add student gradebook function called when the user role is
    the instructor role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict(user_role='Instructor')
    local_response = factory_http_response(handler=local_handler.request)

    with patch.object(
        JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None
    ) as mock_add_user_to_nbgrader_gradebook:
        with patch.object(JupyterHubAPI, 'add_instructor_to_jupyterhub_group', return_value=None):
            with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
                await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert not mock_add_user_to_nbgrader_gradebook.called


@pytest.mark.asyncio()
async def test_setup_course_hook_does_not_call_add_instructor_to_jupyterhub_group_when_role_is_learner(
    setup_course_environ, setup_course_hook_environ
):
    """
    Is the jupyterhub_api add instructor to jupyterhub group function not called when the user role is
    the learner role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict()
    local_response = factory_http_response(handler=local_handler.request)

    with patch.object(JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None):
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(
                JupyterHubAPI, 'add_instructor_to_jupyterhub_group', return_value=None
            ) as mock_add_instructor_to_jupyterhub_group:
                with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
                    await setup_course_hook(local_authenticator, local_handler, local_authentication)
                    assert not mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_initialize_data_dict(setup_course_environ, setup_course_hook_environ):
    """
    Is the data dictionary correctly initialized when properly setting the org env-var and and consistent with the
    course id value in the auth state?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict()
    local_response = factory_http_response(handler=local_handler.request)

    expected_data = {
        'org': 'test-org',
        'course_id': 'intro101',
        'domain': '127.0.0.1',
    }

    with patch.object(JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None):
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
                result = await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert expected_data['course_id'] == result['auth_state']['course_id']
                assert expected_data['org'] == os.environ.get('ORGANIZATION_NAME')
                assert expected_data['domain'] == local_handler.request.host


@pytest.mark.asyncio()
async def test_is_new_course_initiates_rolling_update(setup_course_environ, setup_course_hook_environ):
    """
    If the course is a new setup does it initiate a rolling update?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict()
    local_response = factory_http_response(handler=local_handler.request, body={'is_new_setup': True})

    with patch.object(
        JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
                with patch.object(AsyncHTTPClient, 'fetch', return_value=local_response):
                    await setup_course_hook(local_authenticator, local_handler, local_authentication)
