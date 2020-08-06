import json
import os

from jupyterhub.auth import Authenticator

import pytest

from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient

from unittest.mock import AsyncMock
from unittest.mock import patch

from illumidesk.apis.jupyterhub_api import JupyterHubAPI
from illumidesk.apis.announcement_service import AnnouncementService

from illumidesk.authenticators.authenticator import LTI11Authenticator
from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.authenticators.authenticator import setup_course_hook
from illumidesk.authenticators.utils import LTIUtils


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
async def test_setup_course_hook_raises_environment_error_with_missing_org(
    monkeypatch, make_auth_state_dict, setup_course_hook_environ, make_mock_request_handler
):
    """
    Is an environment error raised when the organization name is missing when calling
    the setup_course_hook function?
    """
    monkeypatch.setenv('ORGANIZATION_NAME', '')
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict()
    with pytest.raises(EnvironmentError):
        await local_authenticator.post_auth_hook(local_authenticator, local_handler, local_authentication)


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_normalize_strings(
    auth_state_dict, setup_course_environ, setup_course_hook_environ, make_mock_request_handler, make_http_response
):
    """
    Does the setup_course_hook return normalized strings for the username and the course_id?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = auth_state_dict

    with patch.object(LTIUtils, 'normalize_string', return_value='intro101') as mock_normalize_string:
        with patch.object(JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None):
            with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
                with patch.object(
                    AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request)
                ):
                    _ = await setup_course_hook(local_authenticator, local_handler, local_authentication)
                    assert mock_normalize_string.called


@pytest.mark.asyncio()
async def test_setup_course_hook_raises_json_decode_error_without_client_fetch_response(
    monkeypatch,
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_mock_request_handler,
    make_http_response,
):
    """
    Does the setup course hook raise a json decode error if the response form the setup course
    microservice is null or empty?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict()

    with patch.object(
        JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(
                AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request, body=None)
            ):
                with pytest.raises(json.JSONDecodeError):
                    await setup_course_hook(local_authenticator, local_handler, local_authentication)


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_student_to_jupyterhub_group_when_role_is_learner(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
):
    """
    Is the jupyterhub_api add student to jupyterhub group function called when the user role is
    the learner role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict()

    with patch.object(
        JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(
                AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request)
            ):
                result = await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert mock_add_student_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_user_to_nbgrader_gradebook_when_role_is_learner(
    monkeypatch,
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_mock_request_handler,
    make_http_response,
):
    """
    Is the jupyterhub_api add user to nbgrader gradebook function called when the user role is
    the learner role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict()

    with patch.object(JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None):
        with patch.object(
            JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None
        ) as mock_add_user_to_nbgrader_gradebook:
            with patch.object(
                AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request)
            ):
                await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert mock_add_user_to_nbgrader_gradebook.called


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_instructor_to_jupyterhub_group_when_role_is_instructor(
    monkeypatch,
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_mock_request_handler,
    make_http_response,
):
    """
    Is the jupyterhub_api add instructor to jupyterhub group function called when the user role is
    the instructor role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict(user_role='Instructor')

    with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
        with patch.object(
            JupyterHubAPI, 'add_instructor_to_jupyterhub_group', return_value=None
        ) as mock_add_instructor_to_jupyterhub_group:
            with patch.object(
                AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request)
            ):
                await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_instructor_to_jupyterhub_group_when_role_is_TeachingAssistant(
    monkeypatch,
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_mock_request_handler,
    make_http_response,
):
    """
    Is the jupyterhub_api add instructor to jupyterhub group function called when the user role is
    the instructor role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict(user_role='urn:lti:role:ims/lis/TeachingAssistant')

    with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
        with patch.object(
            JupyterHubAPI, 'add_instructor_to_jupyterhub_group', return_value=None
        ) as mock_add_instructor_to_jupyterhub_group:
            with patch.object(
                AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request)
            ):
                await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_does_not_call_add_student_to_jupyterhub_group_when_role_is_instructor(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
):
    """
    Is the jupyterhub_api add student to jupyterhub group function called when the user role is
    the instructor role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict(user_role='Instructor')

    with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
        with patch.object(
            JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
        ) as mock_add_student_to_jupyterhub_group:
            with patch.object(
                JupyterHubAPI, 'add_instructor_to_jupyterhub_group', return_value=None
            ) as mock_add_instructor_to_jupyterhub_group:
                with patch.object(
                    AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request)
                ):
                    await setup_course_hook(local_authenticator, local_handler, local_authentication)
                    assert not mock_add_student_to_jupyterhub_group.called
                    assert mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_does_not_call_add_instructor_to_jupyterhub_group_when_role_is_learner(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
):
    """
    Is the jupyterhub_api add instructor to jupyterhub group function not called when the user role is
    the learner role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict()

    with patch.object(JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None):
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(
                JupyterHubAPI, 'add_instructor_to_jupyterhub_group', return_value=None
            ) as mock_add_instructor_to_jupyterhub_group:
                with patch.object(
                    AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request),
                ):
                    await setup_course_hook(local_authenticator, local_handler, local_authentication)
                    assert not mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_initialize_data_dict(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
):
    """
    Is the data dictionary correctly initialized when properly setting the org env-var and and consistent with the
    course id value in the auth state?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict()

    expected_data = {
        'org': 'test-org',
        'course_id': 'intro101',
        'domain': '127.0.0.1',
    }

    with patch.object(JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None):
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(
                AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request)
            ):
                result = await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert expected_data['course_id'] == result['auth_state']['course_id']
                assert expected_data['org'] == os.environ.get('ORGANIZATION_NAME')
                assert expected_data['domain'] == local_handler.request.host


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_announcement_service_when_is_new_setup(
    setup_course_hook_environ, make_auth_state_dict, make_http_response, make_mock_request_handler,
):
    """
    Is the annuncement service called in new setup?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict()

    response_args = {'handler': local_handler.request, 'body': {'is_new_setup': True}}
    with patch.object(
        JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):

            with patch.object(
                AsyncHTTPClient, 'fetch', side_effect=[make_http_response(**response_args), None,],  # noqa: E231
            ):
                AnnouncementService.add_announcement = AsyncMock(return_value=None)

                await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert AnnouncementService.add_announcement.called


@pytest.mark.asyncio()
async def test_is_new_course_initiates_rolling_update(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
):
    """
    If the course is a new setup does it initiate a rolling update?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = make_auth_state_dict()

    response_args = {'handler': local_handler.request, 'body': {'is_new_setup': True}}
    with patch.object(
        JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):

            with patch.object(
                AsyncHTTPClient, 'fetch', side_effect=[make_http_response(**response_args), None,],  # noqa: E231
            ) as mock_client:
                AnnouncementService.add_announcement = AsyncMock(return_value=None)

                await setup_course_hook(local_authenticator, local_handler, local_authentication)
                assert mock_client.called

                mock_client.assert_any_call(
                    'http://setup-course:8000/rolling-update',
                    headers={'Content-Type': 'application/json'},
                    body='',
                    method='POST',
                )

                mock_client.assert_any_call(
                    'http://setup-course:8000',
                    headers={'Content-Type': 'application/json'},
                    body='{"org": "test-org", "course_id": "intro101", "domain": "127.0.0.1"}',
                    method='POST',
                )
