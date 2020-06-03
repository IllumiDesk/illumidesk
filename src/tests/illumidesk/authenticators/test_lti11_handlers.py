import pytest

from unittest.mock import patch

from illumidesk.authenticators.authenticator import LTI11AuthenticateHandler
from tests.illumidesk.mocks import mock_handler


@pytest.mark.asyncio
async def test_lti_11_authenticate_handler_invokes_redirect_method():
    """
    Does the LTI11AuthenticateHandler call the redirect function?
    """
    local_handler = mock_handler(LTI11AuthenticateHandler)
    with patch.object(LTI11AuthenticateHandler, 'redirect', return_value=None) as mock_redirect:
        with patch.object(LTI11AuthenticateHandler, 'login_user', return_value=None):
            await LTI11AuthenticateHandler(local_handler.application, local_handler.request).post()
            assert mock_redirect.called


@pytest.mark.asyncio
async def test_lti_11_authenticate_handler_invokes_login_user_method():
    """
    Does the LTI11AuthenticateHandler call the login_user function?
    """
    local_handler = mock_handler(LTI11AuthenticateHandler)
    with patch.object(LTI11AuthenticateHandler, 'redirect', return_value=None):
        with patch.object(LTI11AuthenticateHandler, 'login_user', return_value=None) as mock_login_user:
            await LTI11AuthenticateHandler(local_handler.application, local_handler.request).post()
            assert mock_login_user.called


@pytest.mark.asyncio
async def test_lti_11_authenticate_handler_invokes_login_user_method():
    """
    Does the LTI11AuthenticateHandler call the login_user function?
    """
    local_handler = mock_handler(LTI11AuthenticateHandler)
    with patch.object(LTI11AuthenticateHandler, 'redirect', return_value=None):
        with patch.object(LTI11AuthenticateHandler, 'login_user', return_value=None) as mock_login_user:
            await LTI11AuthenticateHandler(local_handler.application, local_handler.request).post()
            assert mock_login_user.called
