import pytest

from illumidesk.authenticators.authenticator import LTI11Authenticator, LTI13Authenticator
from illumidesk.grades.senders import LTIGradeSender
from illumidesk.handlers.lms_grades import SendGradesHandler
from unittest.mock import (
    patch,
    PropertyMock,
    Mock,
    MagicMock
)
from tests.illumidesk.mocks import mock_handler
from tornado.web import RequestHandler


@pytest.fixture()
def send_grades_handler_lti11():
    jhub_settings ={
        'authenticator_class': LTI11Authenticator
    }
    request_handler = mock_handler(RequestHandler, **jhub_settings)
    send_grades_handler = SendGradesHandler(request_handler.application, request_handler.request)
    return send_grades_handler


@pytest.fixture()
def send_grades_handler_lti13():
    jhub_settings ={
        'authenticator_class': LTI13Authenticator
    }
    request_handler = mock_handler(RequestHandler, **jhub_settings)
    send_grades_handler = SendGradesHandler(request_handler.application, request_handler.request)
    return send_grades_handler


@pytest.mark.asyncio
@patch('illumidesk.grades.senders.LTIGradeSender.send_grades')
@patch('tornado.web.RequestHandler.write')
async def test_SendGradesHandler_calls_authenticator_class_property(mock_write, mock_send_grades, send_grades_handler_lti11):
    """
    Does the SendGradesHandler uses authenticator_class property to get what authenticator was set?
    """
    with patch.object(SendGradesHandler, 'authenticator_class', callable=PropertyMock) as mock_authenticator_property:
        await send_grades_handler_lti11.post('course_example', 'assignment_test')
        mock_authenticator_property.called


@pytest.mark.asyncio
@patch('illumidesk.grades.senders.LTIGradeSender.send_grades')
@patch('tornado.web.RequestHandler.write')
async def test_SendGradesHandler_authenticator_class_gets_its_value_from_settings(mock_write, mock_send_grades, send_grades_handler_lti11, send_grades_handler_lti13):
    """
    Does the SendGradesHandler.authenticator_class property gets its value from jhub settings?
    """
    assert send_grades_handler_lti11.authenticator_class == LTI11Authenticator
    assert send_grades_handler_lti13.authenticator_class == LTI13Authenticator


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_SendGradesHandler_creates_a_LTIGradeSender_instance_when_LTI11Authenticator_was_set(mock_write, send_grades_handler_lti11):

    with patch('illumidesk.handlers.lms_grades.LTIGradeSender') as mock_lti_grades_sender:
        await send_grades_handler_lti11.post('course_example', 'assignment_test')
        assert mock_lti_grades_sender.called


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_SendGradesHandler_creates_a_LTI13GradeSender_instance_when_LTI13Authenticator_was_set(mock_write, send_grades_handler_lti13):

    with patch('illumidesk.handlers.lms_grades.LTI13GradeSender') as mock_lti13_grades_sender:
        await send_grades_handler_lti13.post('course_example', 'assignment_test')
        assert mock_lti13_grades_sender.called
    
