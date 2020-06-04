from os import chmod
from os import environ

import pytest

from tornado.web import RequestHandler

from unittest.mock import patch

from illumidesk.handlers.lti import LTI13ConfigHandler

from tests.illumidesk.mocks import mock_handler


@pytest.mark.asyncio
async def test_get_method_raises_an_error_without_lti13_private_key():
    """
    Is an environment error raised if the LTI13_PRIVATE_KEY env var is not set
    after calling the handler's method?
    """
    handler = mock_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    with pytest.raises(EnvironmentError):
        await config_handler.get()


@pytest.mark.asyncio
async def test_get_method_raises_permission_error_if_pem_file_is_protected(lti_config_environ):
    """
    Is a permissions error raised if the private key is protected after calling the
    handler's method?
    """
    handler = mock_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # change pem permission
    key_path = environ.get('LTI13_PRIVATE_KEY')
    chmod(key_path, 0o060)
    with pytest.raises(PermissionError):
        await config_handler.get()


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_get_method_reads_the_pem_file(mock_write, lti_config_environ):
    """
    Is the private key written to the output buffer after after calling the handler's
    get method?
    """
    handler = mock_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # this method writes the output to internal buffer
    await config_handler.get()

    assert mock_write.called
