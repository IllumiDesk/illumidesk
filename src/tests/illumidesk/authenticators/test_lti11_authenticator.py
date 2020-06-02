import pytest
import json

from tornado.web import RequestHandler
from tornado.httputil import HTTPServerRequest

from unittest.mock import Mock
from unittest.mock import MagicMock
from unittest.mock import patch

from illumidesk.authenticators.validator import LTI11LaunchValidator
from illumidesk.authenticators.authenticator import LTI11Authenticator
from illumidesk.authenticators.utils import LTIUtils
from tests.illumidesk.factory import factory_lti11_complete_launch_args


@pytest.mark.asyncio
@patch('illumidesk.authenticators.validator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_canvas_fields(lti11_authenticator):
    """
    Do we get a valid username when sending an argument with the custom canvas id?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(arguments=factory_lti11_complete_launch_args('canvas'), headers={}, items=[],),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.validator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_other_lms_vendor(lti11_authenticator,):
    """
    Do we get a valid username with lms vendors other than canvas?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(arguments=factory_lti11_complete_launch_args('moodle'), headers={}, items=[],),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
async def test_authenticator_uses_lti11validator():
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True) as mock_validator:

        authenticator = LTI11Authenticator()
        handler = Mock(spec=RequestHandler)
        request = HTTPServerRequest(method='POST', connection=Mock(),)
        handler.request = request

        handler.request.arguments = factory_lti11_complete_launch_args('lmsvendor')
        handler.request.get_argument = lambda x, strip=True: factory_lti11_complete_launch_args('lmsvendor')[x][
            0
        ].decode()

        _ = await authenticator.authenticate(handler, None)
        assert mock_validator.called


@pytest.mark.asyncio
async def test_authenticator_invokes_validator_with_decoded_dict():
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True) as mock_validator:

        authenticator = LTI11Authenticator()
        handler = Mock(spec=RequestHandler)
        request = HTTPServerRequest(method='POST', uri='/hub', host='example.com')
        handler.request = request
        handler.request.protocol = 'https'
        handler.request.arguments = factory_lti11_complete_launch_args('canvas')
        handler.request.get_argument = lambda x, strip=True: factory_lti11_complete_launch_args('canvas')[x][
            0
        ].decode()

        _ = await authenticator.authenticate(handler, None)
        # check our validator was called
        assert mock_validator.called
        decoded_args = {
            k: handler.request.get_argument(k, strip=False)
            for k, v in factory_lti11_complete_launch_args('canvas').items()
        }
        # check validator was called with correct dict params (decoded)
        mock_validator.assert_called_with('https://example.com/hub', {}, decoded_args)


@pytest.mark.asyncio
@patch('illumidesk.authenticators.validator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_missing_lis_outcome_service_url(lti11_authenticator,):
    """
    Are we able to handle requests with a missing lis_outcome_service_url key?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = factory_lti11_complete_launch_args('canvas', 'Learner')        
        del args['lis_outcome_service_url']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(arguments=args, headers={}, items=[],),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Learner',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.validator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_missing_lis_result_sourcedid(lti11_authenticator,):
    """
    Are we able to handle requests with a missing lis_result_sourcedid key?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = factory_lti11_complete_launch_args('canvas', 'Learner')
        del args['lis_result_sourcedid']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(arguments=args, headers={}, items=[],),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Learner',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_empty_lis_result_sourcedid(lti11_authenticator,):
    """
    Are we able to handle requests with lis_result_sourcedid set to an empty value?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = factory_lti11_complete_launch_args('canvas', 'Learner')
        args['lis_result_sourcedid'] = ''
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(arguments=args, headers={}, items=[],),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Learner',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_empty_lis_outcome_service_url(lti11_authenticator,):
    """
    Are we able to handle requests with lis_outcome_service_url set to an empty value?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = factory_lti11_complete_launch_args('canvas', 'Learner')
        args['lis_outcome_service_url'] = ''
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(arguments=args, headers={}, items=[],),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Learner',
            },
        }
        assert result == expected
