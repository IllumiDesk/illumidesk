from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from tornado.web import RequestHandler

from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.grades.handlers import SendGradesHandler


@pytest.fixture()
def send_grades_handler_lti13(make_mock_request_handler):
    jhub_settings = {"authenticator": LTI13Authenticator}

    async def user_auth_state():
        return []

    def mock_user():
        mock_user = Mock()
        attrs = {
            "get_auth_state.side_effect": user_auth_state,
        }
        mock_user.configure_mock(**attrs)
        return mock_user

    request_handler = make_mock_request_handler(RequestHandler, **jhub_settings)
    send_grades_handler = SendGradesHandler(
        request_handler.application, request_handler.request
    )
    setattr(send_grades_handler, "_jupyterhub_user", mock_user())
    return send_grades_handler


@pytest.mark.asyncio
@patch("tornado.web.RequestHandler.write")
async def test_SendGradesHandler_calls_authenticator_class_property(
    mock_write, send_grades_handler_lti13
):
    """
    Does the SendGradesHandler uses authenticator_class property to get what authenticator was set?
    """
    with patch("illumidesk.grades.handlers.LTI13GradeSender") as mock_sender:
        instance = mock_sender.return_value
        instance.send_grades = AsyncMock()
        await send_grades_handler_lti13.post("course_example", "assignment_test")
        assert mock_sender.called


@pytest.mark.asyncio
@patch("tornado.web.RequestHandler.write")
async def test_SendGradesHandler_authenticator_class_gets_its_value_from_settings(
    mock_write, send_grades_handler_lti13
):
    """
    Does the SendGradesHandler.authenticator_class property gets its value from jhub settings?
    """
    assert send_grades_handler_lti13.authenticator == LTI13Authenticator


@pytest.mark.asyncio
@patch("tornado.web.RequestHandler.write")
async def test_SendGradesHandler_creates_a_LTI13GradeSender_instance_when_LTI13Authenticator_was_set(
    mock_write, send_grades_handler_lti13
):
    """
    Does the SendGradesHandler create a LTI13GradeSender instance for lti13?
    """
    with patch("illumidesk.grades.handlers.LTI13GradeSender") as mock_sender:
        instance = mock_sender.return_value
        instance.send_grades = AsyncMock()
        await send_grades_handler_lti13.post("course_example", "assignment_test")
        assert mock_sender.called


@pytest.mark.asyncio
@patch("tornado.web.RequestHandler.write")
async def test_SendGradesHandler_calls_write_method(
    mock_write, send_grades_handler_lti13
):
    """
    Does the SendGradesHandler call write base method?
    """
    with patch("illumidesk.grades.handlers.LTI13GradeSender") as mock_sender:
        instance = mock_sender.return_value
        instance.send_grades = AsyncMock()
        await send_grades_handler_lti13.post("course_example", "assignment_test")
        assert mock_write.called
