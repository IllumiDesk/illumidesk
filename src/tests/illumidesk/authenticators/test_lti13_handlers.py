import pytest

from tornado.web import MissingArgumentError

from illumidesk.authenticators.handlers import LTI13LoginHandler
from illumidesk.authenticators.authenticator import LTI13Authenticator

from tests.illumidesk.mocks import mock_handler
from tests.illumidesk.factory import factory_auth_state_dict


@pytest.mark.asyncio
async def test_lti_13_login_handler_no_args_body_raises_missing_argument_error():
    """
    Does the LTI13LoginHandler raise a missing argument error if request body doesn't have any
    arguments?
    """
    local_authenticator = LTI13Authenticator()
    local_handler = mock_handler(LTI13LoginHandler, authenticator=local_authenticator)
    local_authentication = factory_auth_state_dict()
    with pytest.raises(MissingArgumentError):
        await LTI13LoginHandler(local_handler.application, local_handler.request).post()
