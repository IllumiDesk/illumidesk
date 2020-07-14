import hashlib

import pytest

from unittest.mock import patch
from unittest.mock import MagicMock

from illumidesk.authenticators.handlers import LTI13LoginHandler
from illumidesk.authenticators.authenticator import LTI13LaunchValidator
from illumidesk.authenticators.utils import LTIUtils


@pytest.mark.asyncio
async def test_lti_13_login_handler_empty_authorize_url_env_var_raises_environment_error(
    monkeypatch, lti13_login_params, lti13_login_params_dict, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler raise a missing argument error if request body doesn't have any
    arguments?
    """
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', '')
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    local_utils = LTIUtils()
    with patch.object(
        LTIUtils, 'convert_request_to_dict', return_value=lti13_login_params_dict
    ) as mock_convert_request_to_dict:
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            with patch.object(LTI13LoginHandler, 'redirect', return_value=None):
                with pytest.raises(EnvironmentError):
                    LTI13LoginHandler(local_handler.application, local_handler.request).post()


@pytest.mark.asyncio
async def test_lti_13_login_handler_invokes_convert_request_to_dict_method(
    monkeypatch, lti13_login_params, lti13_login_params_dict, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler call the LTIUtils convert_request_to_dict function once it
    receiving the post request?
    """
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', 'http://my.lms.platform/api/lti/authorize_redirect')
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    with patch.object(
        LTIUtils, 'convert_request_to_dict', return_value=lti13_login_params_dict
    ) as mock_convert_request_to_dict:
        with patch.object(LTI13LaunchValidator, 'validate_login_request', return_value=True):
            with patch.object(LTI13LoginHandler, 'authorize_redirect', return_value=None):
                LTI13LoginHandler(local_handler.application, local_handler.request).post()
                assert mock_convert_request_to_dict.called


@pytest.mark.asyncio
async def test_lti_13_login_handler_invokes_validate_login_request_method(
    monkeypatch, lti13_auth_params, lti13_auth_params_dict, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler call the LTI13LaunchValidator validate_login_request function once it
    receiving the post request?
    """
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', 'http://my.lms.platform/api/lti/authorize_redirect')
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    local_utils = LTIUtils()
    with patch.object(LTIUtils, 'convert_request_to_dict', return_value=lti13_auth_params_dict):
        with patch.object(
            LTI13LaunchValidator, 'validate_login_request', return_value=True
        ) as mock_validate_login_request:
            with patch.object(LTI13LoginHandler, 'authorize_redirect', return_value=None):
                LTI13LoginHandler(local_handler.application, local_handler.request).post()
                assert mock_validate_login_request.called


@pytest.mark.asyncio
async def test_lti_13_login_handler_invokes_redirect_method(monkeypatch, lti13_auth_params, make_mock_request_handler):
    """
    Does the LTI13LoginHandler call the redirect function once it
    receiving the post request?
    """
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', 'http://my.lms.platform/api/lti/authorize_redirect')
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    local_utils = LTIUtils()
    local_utils.convert_request_to_dict(lti13_auth_params)
    with patch.object(
        LTIUtils, 'convert_request_to_dict', return_value=local_utils.convert_request_to_dict(lti13_auth_params)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_login_request', return_value=True):
            with patch.object(LTI13LoginHandler, 'authorize_redirect', return_value=None) as mock_redirect:
                LTI13LoginHandler(local_handler.application, local_handler.request).post()
                assert mock_redirect.called


@pytest.mark.asyncio
async def test_lti_13_login_handler_sets_vars_for_redirect(
    monkeypatch, lti13_auth_params, lti13_auth_params_dict, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler correctly set all variables needed for the redict method
    after receiving it from the validator?
    """
    expected = lti13_auth_params_dict
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', 'http://my.lms.platform/api/lti/authorize_redirect')
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    local_utils = LTIUtils()
    with patch.object(LTIUtils, 'convert_request_to_dict', return_value=lti13_auth_params_dict):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            with patch.object(LTI13LoginHandler, 'redirect', return_value=None):
                assert expected['client_id'] == '125900000000000081'
                assert expected['redirect_uri'] == 'https://acme.illumidesk.com/hub/oauth_callback'
                assert (
                    expected['lti_message_hint']
                    == 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2ZXJpZmllciI6IjFlMjk2NjEyYjZmMjdjYmJkZTg5YmZjNGQ1ZmQ5ZDBhMzhkOTcwYzlhYzc0NDgwYzdlNTVkYzk3MTQyMzgwYjQxNGNiZjMwYzM5Nzk1Y2FmYTliOWYyYTgzNzJjNzg3MzAzNzAxZDgxMzQzZmRmMmIwZDk5ZTc3MWY5Y2JlYWM5IiwiY2FudmFzX2RvbWFpbiI6ImlsbHVtaWRlc2suaW5zdHJ1Y3R1cmUuY29tIiwiY29udGV4dF90eXBlIjoiQ291cnNlIiwiY29udGV4dF9pZCI6MTI1OTAwMDAwMDAwMDAwMTM2LCJleHAiOjE1OTE4MzMyNTh9.uYHinkiAT5H6EkZW9D7HJ1efoCmRpy3Id-gojZHlUaA'
                )
                assert expected['login_hint'] == '185d6c59731a553009ca9b59ca3a885104ecb4ad'
                assert (
                    expected['state']
                    == 'eyJzdGF0ZV9pZCI6ICI2ZjBlYzE1NjlhM2E0MDJkYWM2MTYyNjM2MWQwYzEyNSIsICJuZXh0X3VybCI6ICIvIn0='
                )
                assert expected['nonce'] == '38048502278109788461591832959'


@pytest.mark.asyncio
async def test_lti_13_login_handler_nonce(monkeypatch, lti13_auth_params, lti13_auth_params_dict):
    """
    Do we get the expected nonce value result after hashing the state and returning the
    hexdigest?
    """
    args_dict = lti13_auth_params_dict
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', 'http://my.lms.platform/api/lti/authorize_redirect')
    local_handler = MagicMock(spec=LTI13LoginHandler)
    local_handler.request = lti13_auth_params
    local_utils = LTIUtils()
    with patch.object(LTIUtils, 'convert_request_to_dict', return_value=lti13_auth_params_dict):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            with patch.object(LTI13LoginHandler, 'redirect', return_value=None):
                expected = hashlib.sha256(
                    b'eyJzdGF0ZV9pZCI6ICI2ZjBlYzE1NjlhM2E0MDJkYWM2MTYyNjM2MWQwYzEyNSIsICJuZXh0X3VybCI6ICIvIn0='
                ).hexdigest()
                result = hashlib.sha256(args_dict['state'].encode()).hexdigest()
                assert expected == result
