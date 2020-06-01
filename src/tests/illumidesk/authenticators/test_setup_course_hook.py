from json import JSONDecodeError

from jupyterhub.auth import Authenticator

import pytest

from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient, HTTPResponse

from unittest.mock import MagicMock
from unittest.mock import patch

from illumidesk.apis.jupyterhub_api import JupyterHubAPI
from illumidesk.authenticators.authenticator import LTI11Authenticator
from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.authenticators.authenticator import setup_course_hook
from illumidesk.apis.jupyterhub_api import JupyterHubAPI

from tests.illumidesk.mocks import mock_handler
from tests.illumidesk.factory import factory_auth_state_dict


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
async def test_setup_course_hook_calls_add_student_to_jupyterhub_group_when_role_is_learner(
    monkeypatch, setup_course_environ, setup_course_hook_environ
):
    """
    Is the jupyterhub_api add student to jupyterhub group function called when the user role is
    the learner role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = mock_handler(RequestHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict()
    local_response = MagicMock(spec=HTTPResponse)
    local_response = HTTPResponse(local_handler.request, code=200, effective_url='localhost')

    async def result_async():
        return local_response

    local_authentication['auth_state']['user_role'] == 'Learner'
    with patch.object(
        JupyterHubAPI, 'add_student_to_jupyterhub_group', return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(JupyterHubAPI, 'add_user_to_nbgrader_gradebook', return_value=None):
            with patch.object(AsyncHTTPClient, 'fetch', return_value=result_async()):
                with pytest.raises(JSONDecodeError):
                    await setup_course_hook(local_authenticator, local_handler, local_authentication)
