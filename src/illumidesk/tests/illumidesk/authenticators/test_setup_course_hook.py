import os
from unittest.mock import patch

import pytest
from jupyterhub.auth import Authenticator
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler

from illumidesk.apis.jupyterhub_api import JupyterHubAPI
from illumidesk.apis.nbgrader_service import NbGraderServiceHelper
from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.authenticators.authenticator import setup_course_hook


@pytest.mark.asyncio
async def test_setup_course_hook_is_assigned_to_lti13_authenticator_post_auth_hook():
    """
    Does the setup course hook get assigned to the post_auth_hook for the LTI13Authenticator?
    """
    authenticator = LTI13Authenticator(post_auth_hook=setup_course_hook)
    assert authenticator.post_auth_hook == setup_course_hook


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_student_to_jupyterhub_group_when_role_is_learner(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
    mock_nbhelper,
):
    """
    Is the jupyterhub_api add student to jupyterhub group function called when the user role is
    the learner role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(
        RequestHandler, authenticator=local_authenticator
    )
    local_authentication = make_auth_state_dict()

    with patch.object(
        JupyterHubAPI, "add_student_to_jupyterhub_group", return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(
            AsyncHTTPClient,
            "fetch",
            return_value=make_http_response(handler=local_handler.request),
        ):
            result = await setup_course_hook(
                local_authenticator, local_handler, local_authentication
            )
            assert mock_add_student_to_jupyterhub_group.called


@patch("shutil.chown")
@patch("pathlib.Path.mkdir")
@patch("illumidesk.apis.nbgrader_service.Gradebook")
@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_user_to_nbgrader_gradebook_when_role_is_learner(
    mock_mkdir,
    mock_chown,
    mock_gradebook,
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
    local_handler = make_mock_request_handler(
        RequestHandler, authenticator=local_authenticator
    )
    local_authentication = make_auth_state_dict()

    with patch.object(
        JupyterHubAPI, "add_student_to_jupyterhub_group", return_value=None
    ):
        with patch.object(
            NbGraderServiceHelper, "add_user_to_nbgrader_gradebook", return_value=None
        ) as mock_add_user_to_nbgrader_gradebook:
            with patch.object(
                AsyncHTTPClient,
                "fetch",
                return_value=make_http_response(handler=local_handler.request),
            ):
                await setup_course_hook(
                    local_authenticator, local_handler, local_authentication
                )
                assert mock_add_user_to_nbgrader_gradebook.called


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_instructor_to_jupyterhub_group_when_role_is_instructor(
    monkeypatch,
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_mock_request_handler,
    make_http_response,
    mock_nbhelper,
):
    """
    Is the jupyterhub_api add instructor to jupyterhub group function called when the user role is
    the instructor role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(
        RequestHandler, authenticator=local_authenticator
    )
    local_authentication = make_auth_state_dict(user_role="Instructor")

    with patch.object(
        JupyterHubAPI, "add_instructor_to_jupyterhub_group", return_value=None
    ) as mock_add_instructor_to_jupyterhub_group:
        with patch.object(
            AsyncHTTPClient,
            "fetch",
            return_value=make_http_response(handler=local_handler.request),
        ):
            await setup_course_hook(
                local_authenticator, local_handler, local_authentication
            )
            assert mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_calls_add_instructor_to_jupyterhub_group_when_role_is_TeachingAssistant(
    monkeypatch,
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_mock_request_handler,
    make_http_response,
    mock_nbhelper,
):
    """
    Is the jupyterhub_api add instructor to jupyterhub group function called when the user role is
    the instructor role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(
        RequestHandler, authenticator=local_authenticator
    )
    local_authentication = make_auth_state_dict(
        user_role="urn:lti:role:ims/lis/TeachingAssistant"
    )

    with patch.object(
        JupyterHubAPI, "add_instructor_to_jupyterhub_group", return_value=None
    ) as mock_add_instructor_to_jupyterhub_group:
        with patch.object(
            AsyncHTTPClient,
            "fetch",
            return_value=make_http_response(handler=local_handler.request),
        ):
            await setup_course_hook(
                local_authenticator, local_handler, local_authentication
            )
            assert mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_does_not_call_add_student_to_jupyterhub_group_when_role_is_instructor(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
    mock_nbhelper,
):
    """
    Is the jupyterhub_api add student to jupyterhub group function called when the user role is
    the instructor role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(
        RequestHandler, authenticator=local_authenticator
    )
    local_authentication = make_auth_state_dict(user_role="Instructor")

    with patch.object(
        JupyterHubAPI, "add_student_to_jupyterhub_group", return_value=None
    ) as mock_add_student_to_jupyterhub_group:
        with patch.object(
            JupyterHubAPI, "add_instructor_to_jupyterhub_group", return_value=None
        ) as mock_add_instructor_to_jupyterhub_group:
            with patch.object(
                AsyncHTTPClient,
                "fetch",
                return_value=make_http_response(handler=local_handler.request),
            ):
                await setup_course_hook(
                    local_authenticator, local_handler, local_authentication
                )
                assert not mock_add_student_to_jupyterhub_group.called
                assert mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_does_not_call_add_instructor_to_jupyterhub_group_when_role_is_learner(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
    mock_nbhelper,
):
    """
    Is the jupyterhub_api add instructor to jupyterhub group function not called when the user role is
    the learner role?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(
        RequestHandler, authenticator=local_authenticator
    )
    local_authentication = make_auth_state_dict()

    with patch.object(
        JupyterHubAPI, "add_student_to_jupyterhub_group", return_value=None
    ):
        with patch.object(
            JupyterHubAPI, "add_instructor_to_jupyterhub_group", return_value=None
        ) as mock_add_instructor_to_jupyterhub_group:
            with patch.object(
                AsyncHTTPClient,
                "fetch",
                return_value=make_http_response(handler=local_handler.request),
            ):
                await setup_course_hook(
                    local_authenticator, local_handler, local_authentication
                )
                assert not mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_initialize_data_dict(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
    mock_nbhelper,
):
    """
    Is the data dictionary correctly initialized when properly setting the org env-var and and consistent with the
    course id value in the auth state?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(
        RequestHandler, authenticator=local_authenticator
    )
    local_authentication = make_auth_state_dict()

    expected_data = {
        "org": "test-org",
        "course_id": "intro101",
        "domain": "127.0.0.1",
    }

    with patch.object(
        JupyterHubAPI, "add_student_to_jupyterhub_group", return_value=None
    ):
        with patch.object(
            AsyncHTTPClient,
            "fetch",
            return_value=make_http_response(handler=local_handler.request),
        ):
            result = await setup_course_hook(
                local_authenticator, local_handler, local_authentication
            )
            assert expected_data["course_id"] == result["auth_state"]["course_id"]
            assert expected_data["org"] == os.environ.get("ORGANIZATION_NAME")
            assert expected_data["domain"] == local_handler.request.host


@pytest.mark.asyncio()
async def test_setup_course_hook_does_not_call_add_instructor_to_jupyterhub_group_when_role_is_learner(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
    mock_nbhelper,
):
    """
    Is the register_new_service function called when the user_role is learner or student?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(
        RequestHandler, authenticator=local_authenticator
    )
    local_authentication = make_auth_state_dict()

    with patch.object(
        NbGraderServiceHelper, "add_user_to_nbgrader_gradebook", return_value=None
    ):
        with patch.object(
            JupyterHubAPI, "add_student_to_jupyterhub_group", return_value=None
        ):
            with patch.object(
                JupyterHubAPI, "add_instructor_to_jupyterhub_group", return_value=None
            ) as mock_add_instructor_to_jupyterhub_group:
                with patch.object(
                    AsyncHTTPClient,
                    "fetch",
                    return_value=make_http_response(handler=local_handler.request),
                ):
                    await setup_course_hook(
                        local_authenticator, local_handler, local_authentication
                    )
                    assert not mock_add_instructor_to_jupyterhub_group.called


@pytest.mark.asyncio()
async def test_setup_course_hook_does_not_call_add_instructor_to_jupyterhub_group_when_role_is_learner(
    setup_course_environ,
    setup_course_hook_environ,
    make_auth_state_dict,
    make_http_response,
    make_mock_request_handler,
    mock_nbhelper,
):
    """
    Is the register_new_service function called when the user_role is learner or student?
    """
    local_authenticator = Authenticator(post_auth_hook=setup_course_hook)
    local_handler = make_mock_request_handler(
        RequestHandler, authenticator=local_authenticator
    )
    local_authentication = make_auth_state_dict()

    with patch.object(
        NbGraderServiceHelper, "add_user_to_nbgrader_gradebook", return_value=None
    ):
        with patch.object(
            JupyterHubAPI, "add_student_to_jupyterhub_group", return_value=None
        ):
            with patch.object(
                JupyterHubAPI, "add_instructor_to_jupyterhub_group", return_value=None
            ) as mock_add_instructor_to_jupyterhub_group:
                with patch.object(
                    AsyncHTTPClient,
                    "fetch",
                    return_value=make_http_response(handler=local_handler.request),
                ):
                    await setup_course_hook(
                        local_authenticator, local_handler, local_authentication
                    )
                    assert not mock_add_instructor_to_jupyterhub_group.called
