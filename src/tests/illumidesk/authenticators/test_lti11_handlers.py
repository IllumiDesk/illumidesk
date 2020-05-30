import pytest

from unittest.mock import patch

from illumidesk.authenticators.authenticator import LTI11AuthenticateHandler
from tests.illumidesk.mocks import mock_handler


@pytest.mark.asyncio
async def test_lti11_authenticate_handler_invokes_login_user_method():
    """
    Does the authenticate handler invoke the login_user method?
    """
    local_handler = mock_handler(LTI11AuthenticateHandler)
    with patch.object(LTI11AuthenticateHandler, 'redirect', return_value=None):
        with patch.object(LTI11AuthenticateHandler, 'login_user', return_value=None) as mock_login_user:
            await LTI11AuthenticateHandler(local_handler.application, local_handler.request).post()
            assert mock_login_user.called
