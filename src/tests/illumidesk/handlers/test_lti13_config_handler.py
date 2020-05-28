from os import chmod, environ
import pytest

from Crypto.PublicKey import RSA
from tests.illumidesk.mocks import mock_handler
from tornado.web import RequestHandler
from unittest.mock import patch

from illumidesk.handlers.lti import LTI13ConfigHandler
from illumidesk.authenticators.authenticator import LTI11Authenticator


@pytest.fixture
def pem_file(tmp_path):
    key = RSA.generate(2048)
    key_path = f'{tmp_path}/private.key'
    with open(key_path, 'wb') as content_file:
        content_file.write(key.exportKey('PEM'))
    return key_path

@pytest.fixture(scope="function")
def lti_config_environ(monkeypatch, pem_file):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('LTI13_PRIVATE_KEY', pem_file)

@pytest.mark.asyncio
async def test_get_method_raises_an_error_without_LTI13_PRIVATE_KEY():
    handler = mock_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    with pytest.raises(EnvironmentError):
        await config_handler.get()


@pytest.mark.asyncio
async def test_get_method_raises_permission_error_if_pem_file_is_protected(lti_config_environ):
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
    handler = mock_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    print(handler.__dict__)
    # the next method only write the output to internal buffer
    await config_handler.get()
    
    assert mock_write.called