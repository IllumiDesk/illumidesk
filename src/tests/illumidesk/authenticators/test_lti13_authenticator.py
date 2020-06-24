import pytest

from tornado.web import RequestHandler

from unittest.mock import patch

from illumidesk.authenticators.validator import LTI13LaunchValidator
from illumidesk.authenticators.authenticator import LTI13Authenticator

from tests.illumidesk.mocks import mock_handler
from tests.illumidesk.factory import dummy_lti13_id_token_complete
from tests.illumidesk.factory import dummy_lti13_id_token_empty_roles
from tests.illumidesk.factory import dummy_lti13_id_token_instructor_role
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_email
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_name
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_given_name
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_family_name
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_person_sourcedid
from tests.illumidesk.factory import factory_lti13_resource_link_request


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_handler_get_argument():
    """
    Does the authenticator invoke the RequestHandler get_argument method?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        request_handler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        _ = await authenticator.authenticate(request_handler, None)
        assert mock_get_argument.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_jwt_verify_and_decode():
    """
    Does the authenticator invoke the LTI13Validator jwt_verify_and_decode method?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'jwt_verify_and_decode', return_value=factory_lti13_resource_link_request()
        ) as mock_verify_and_decode:
            _ = await authenticator.authenticate(request_handler, None)
            assert mock_verify_and_decode.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_validate_launch_request():
    """
    Does the authenticator invoke the LTI13Validator validate_launch_request method?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            _ = await authenticator.authenticate(request_handler, None)
            assert mock_verify_launch_request.called


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_valid_email():
    """
    Do we get a valid username when only including an email to the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_email.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['name'] == expected['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_with_name():
    """
    Do we get a valid username when only including the name in the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_name.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['name'] == expected['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_with_given_name():
    """
    Do we get a valid username when only including the given name in the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_given_name.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'foobar',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['name'] == expected['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_family_name():
    """
    Do we get a valid username when only including the family name in the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_family_name.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'bar',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['name'] == expected['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_person_sourcedid():
    """
    Do we get a valid username when only including lis person sourcedid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_person_sourcedid.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'abc123',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['name'] == expected['name']


@pytest.mark.asyncio
async def test_authenticator_returns_course_id_in_auth_state_with_valid_resource_link_request():
    """
    Do we get a valid course_id when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['auth_state']['course_id'] == expected['auth_state']['course_id']


@pytest.mark.asyncio
async def test_authenticator_returns_lms_user_id_in_auth_state_with_valid_resource_link_request():
    """
    Do we get a valid lms_user_id in the auth_state when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': '8171934b-f5e2-4f4e-bdbd-6d798615b93e', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['auth_state']['lms_user_id'] == expected['auth_state']['lms_user_id']


@pytest.mark.asyncio
async def test_authenticator_returns_learner_role_in_auth_state_with_valid_resource_link_request():
    """
    Do we set the learner role in the auth_state when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['auth_state']['user_role'] == expected['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_instructor_role_in_auth_state_with_valid_resource_link_request():
    """
    Do we set the instructor role in the auth_state when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_instructor_role.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {
                    'course_id': 'intro101',
                    'lms_user_id': 'foo',
                    'user_role': 'Instructor',
                },  # noqa: E231
            }
            assert result['auth_state']['user_role'] == expected['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_learner_role_in_auth_state_with_empty_roles():
    """
    Do we set the learner role in the auth_state when receiving resource link request
    with empty roles?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_empty_roles.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(request_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['auth_state']['user_role'] == expected['auth_state']['user_role']
