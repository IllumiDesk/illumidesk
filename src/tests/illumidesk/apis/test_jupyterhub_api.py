import pytest
import os
import uuid
from illumidesk.apis.jupyterhub_api import JupyterHubAPI
from tests.illumidesk.conftest import jupyterhub_api_environ

def test_initializer_raises_error_without_JUPYTERHUB_API_TOKEN_env():
    """
    Does initializer raise an error when 'JUPYTERHUB_API_TOKEN' was not set?
    """
    with pytest.raises(EnvironmentError):
        JupyterHubAPI()

def test_initializer_raises_error_without_JUPYTERHUB_API_URL_env():
    """
    Does initializer raise an error when 'JUPYTERHUB_API_URL' was not set?
    """
    with pytest.raises(EnvironmentError):
        JupyterHubAPI()

def test_initializer_sets_http_client(jupyterhub_api_environ):
    """
    Does initializer set a httpclient instance?
    """
    sut = JupyterHubAPI()
    assert sut.client is not None

def test_initializer_sets_api_token_from_envvar(jupyterhub_api_environ):
    """
    Does initializer set the api token correctly?
    """
    sut = JupyterHubAPI()
    assert sut.token is not None
    assert sut.token == os.environ.get('JUPYTERHUB_API_TOKEN')

def test_initializer_sets_api_root_url_from_envvar(jupyterhub_api_environ):
    """
    Does initializer set the api url?
    """
    sut = JupyterHubAPI()
    assert sut.api_root_url is not None
    assert sut.api_root_url == os.environ.get('JUPYTERHUB_API_URL')

def test_initializer_sets_headers_to_make_requests(jupyterhub_api_environ):
    """
    Does initializer set the api url?
    """
    sut = JupyterHubAPI()
    assert sut.default_headers is not None
    assert type(sut.default_headers) is dict
    assert sut.default_headers['Authorization'] == f'token {os.environ.get("JUPYTERHUB_API_TOKEN")}'

@pytest.mark.asyncio
async def test_create_group_raises_error_with_group_empty(jupyterhub_api_environ):
    """
    Does create_group method accept a group_name empty?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().create_group('')
