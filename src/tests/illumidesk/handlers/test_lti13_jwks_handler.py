from os import chmod
from os import environ
import pytest

from illumidesk.handlers.lti import LTI13JWKSHandler
from tests.illumidesk.mocks import mock_handler
from tornado.web import RequestHandler


@pytest.mark.asyncio
async def test_get_method_raises_permission_error_if_pem_file_is_protected(lti_config_environ):
    """
    Is a permission error raised if the private key is protected after calling the
    handler's method?
    """
    handler = mock_handler(RequestHandler)
    config_handler = LTI13JWKSHandler(handler.application, handler.request)
    # change pem permission
    key_path = environ.get('LTI13_PRIVATE_KEY')
    chmod(key_path, 0o060)
    with pytest.raises(PermissionError):
        await config_handler.get()


@pytest.mark.asyncio
async def test_get_method_raises_an_error_without_lti13_private_key():
    """
    Is an environment error raised if the LTI13_PRIVATE_KEY env var is not set
    after calling the handler's method?
    """
    handler = mock_handler(RequestHandler)
    config_handler = LTI13JWKSHandler(handler.application, handler.request)
    with pytest.raises(EnvironmentError):
        await config_handler.get()