import pytest

from tornado.web import MissingArgumentError

from illumidesk.authenticators.handlers import LTI13LoginHandler
from illumidesk.authenticators.authenticator import LTI13Authenticator

from tests.illumidesk.mocks import mock_handler


@pytest.mark.asyncio
async def test_lti_13_login_handler_no_args_body_raises_missing_argument_error(lti13_auth_params):
    """
    Does the LTI13LoginHandler raise a missing argument error if request body doesn't have any
    arguments?
    """
    local_authenticator = LTI13Authenticator()
    local_handler = mock_handler(LTI13LoginHandler, authenticator=local_authenticator)
    with pytest.raises(MissingArgumentError):
        await LTI13LoginHandler(local_handler.application, local_handler.request).post()
