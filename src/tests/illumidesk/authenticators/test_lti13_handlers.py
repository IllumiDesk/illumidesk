import pytest

from unittest.mock import patch

from illumidesk.authenticators.handlers import LTI13LoginHandler

from tests.illumidesk.mocks import mock_handler


@pytest.mark.asyncio
async def test_lti13_login_handler_calls_get_argument_method():

    local_handler = mock_handler(LTI13LoginHandler)
    with patch.object(LTI13LoginHandler, 'redirect', return_value=None):
        with patch.object(LTI13LoginHandler, 'login_user', return_value=None) as mock_login_user:
            await LTI13LoginHandler(local_handler.application, local_handler.request).post()
            assert mock_login_user.called
