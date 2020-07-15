import pytest

from tornado.web import RequestHandler

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch
from unittest.mock import PropertyMock

from illumidesk.authenticators.authenticator import LTI11Authenticator
from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.grades.senders import LTIGradeSender
from illumidesk.grades.handlers import SendGradesHandler


@pytest.fixture()
def send_grades_handler_lti11(make_mock_request_handler):
    jhub_settings = {'authenticator_class': LTI11Authenticator}
    request_handler = make_mock_request_handler(RequestHandler, **jhub_settings)
    send_grades_handler = SendGradesHandler(request_handler.application, request_handler.request)
    return send_grades_handler


@pytest.fixture()
def send_grades_handler_lti13(make_mock_request_handler):
    jhub_settings = {'authenticator_class': LTI13Authenticator}

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
    send_grades_handler = SendGradesHandler(request_handler.application, request_handler.request)
    setattr(send_grades_handler, '_jupyterhub_user', mock_user())
    return send_grades_handler


@pytest.mark.asyncio
@patch('illumidesk.grades.senders.LTI13GradeSender.send_grades')
@patch('tornado.web.RequestHandler.write')
async def test_SendGradesHandler_calls_authenticator_class_property(
    mock_write, send_grades_handler_lti13, send_grades_handler_lti11
):
    """
    Does the SendGradesHandler uses authenticator_class property to get what authenticator was set?
    """
    with patch('illumidesk.grades.handlers.LTI13GradeSender') as mock_sender:
        instance = mock_sender.return_value
        instance.send_grades = AsyncMock()
        mock_authenticator_class = PropertyMock(return_value=LTI13Authenticator)
        mock_sender.authenticator_class = mock_authenticator_class
        await send_grades_handler_lti13.post('course_example', 'assignment_test')
        mock_authenticator_class.called

    with patch('illumidesk.grades.handlers.LTIGradeSender') as mock_sender:
        instance = mock_sender.return_value
        instance.send_grades = AsyncMock()
        mock_authenticator_class = PropertyMock(return_value=LTI13Authenticator)
        mock_sender.authenticator_class = mock_authenticator_class
        await send_grades_handler_lti11.post('course_example', 'assignment_test')
        mock_authenticator_class.called


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_SendGradesHandler_authenticator_class_gets_its_value_from_settings(
    mock_write, send_grades_handler_lti11, send_grades_handler_lti13
):
    """
    Does the SendGradesHandler.authenticator_class property gets its value from jhub settings?
    """
    assert send_grades_handler_lti11.authenticator_class == LTI11Authenticator
    assert send_grades_handler_lti13.authenticator_class == LTI13Authenticator


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_SendGradesHandler_creates_a_LTIGradeSender_instance_when_LTI11Authenticator_was_set(
    mock_write, send_grades_handler_lti11
):
    """
    Does the SendGradesHandler create a LTIGradeSender instance for lti11?
    """
    with patch.object(LTIGradeSender, 'send_grades', return_value=None) as mock_lti_grades_sender:
        await send_grades_handler_lti11.post('course_example', 'assignment_test')
        assert mock_lti_grades_sender.called


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_SendGradesHandler_creates_a_LTI13GradeSender_instance_when_LTI13Authenticator_was_set(
    mock_write, send_grades_handler_lti13
):
    """
    Does the SendGradesHandler create a LTI13GradeSender instance for lti13?
    """
    with patch('illumidesk.grades.handlers.LTI13GradeSender') as mock_sender:
        instance = mock_sender.return_value
        instance.send_grades = AsyncMock()
        await send_grades_handler_lti13.post('course_example', 'assignment_test')
        assert mock_sender.called


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_SendGradesHandler_calls_write_method(mock_write, send_grades_handler_lti13):
    """
    Does the SendGradesHandler call write base method?
    """
    with patch('illumidesk.grades.handlers.LTI13GradeSender') as mock_sender:
        instance = mock_sender.return_value
        instance.send_grades = AsyncMock()
        await send_grades_handler_lti13.post('course_example', 'assignment_test')
        assert mock_write.called
