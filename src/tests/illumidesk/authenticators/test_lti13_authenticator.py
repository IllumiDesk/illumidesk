import pytest

from unittest.mock import patch

from illumidesk.authenticators.validator import LTI13LaunchValidator
from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.authenticators.handlers import LTI13LoginHandler

from tests.illumidesk.mocks import mock_handler
from tests.illumidesk.factory import dummy_lti13_id_token_complete
from tests.illumidesk.factory import dummy_lti13_id_token_missing_email
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_email_and_given_name
from tests.illumidesk.factory import dummy_lti13_id_token_instructor_role
from tests.illumidesk.factory import dummy_lti13_id_token_empty_roles
from tests.illumidesk.factory import factory_lti13_resource_link_request


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13_login_handler_get_argument():
    """
    Does the authenticator invoke the LTI13LoginHandler get_argument method?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        _ = await authenticator.authenticate(login_handler, None)

        assert mock_get_argument.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_jwt_verify_and_decode():
    """
    Does the authenticator invoke the LTI13Validator jwt_verify_and_decode method?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'jwt_verify_and_decode', return_value=factory_lti13_resource_link_request()
        ) as mock_verify_and_decode:
            _ = await authenticator.authenticate(login_handler, None)

            assert mock_verify_and_decode.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_validate_launch_request():
    """
    Does the authenticator invoke the LTI13Validator validate_launch_request method?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            _ = await authenticator.authenticate(login_handler, None)

    assert mock_verify_launch_request.called


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_valid_email():
    """
    Do we get a valid username when adding a valid email with the resource link request?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(login_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['name'] == expected['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_missing_email_and_valid_given_name():
    """
    Do we get a valid username when sending a JWT token with a missing email but with a valid given
    name with the resource link request?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_missing_email.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(login_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['name'] == expected['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_missing_email_missing_given_name_and_valid_person_sourcedid():
    """
    Do we get a valid username when sending a JWT token with a missing email, missing given name, and valid person_sourcedid
    with the resource link request?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_email_and_given_name.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(login_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['name'] == expected['name']


@pytest.mark.asyncio
async def test_authenticator_returns_instructor_role_in_auth_state_with_valid_resource_link_request():
    """
    Do we get a valid instructor role in the auth_state when receiving a roles claim with the instructor role?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_instructor_role.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(login_handler, None)
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
async def test_authenticator_returns_learner_role_in_auth_state_without_roles_in_valid_resource_link_request():
    """
    Do we get a valid learner role in the auth_state when the roles claim is empty?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_empty_roles.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(login_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['auth_state']['user_role'] == expected['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_course_id_in_auth_state_with_valid_resource_link_request():
    """
    Do we get a valid course_id when receiving with a valid request?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(login_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['auth_state']['course_id'] == expected['auth_state']['course_id']


@pytest.mark.asyncio
async def test_authenticator_returns_learner_role_in_auth_state_with_valid_resource_link_request():
    """
    Do we set the learner role in the auth_state when the roles claim is set with the learner role?
    """
    authenticator = LTI13Authenticator()
    login_handler = mock_handler(LTI13LoginHandler, authenticator=authenticator)
    with patch.object(
        LTI13LoginHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_launch_request:
            result = await authenticator.authenticate(login_handler, None)
            expected = {
                'name': 'foo',
                'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
            }
            assert result['auth_state']['user_role'] == expected['auth_state']['user_role']
