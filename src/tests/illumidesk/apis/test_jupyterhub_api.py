import json
import pytest
import os
import uuid

from unittest.mock import patch

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

async def request_async_result(endpoint, **kwargs):
    return True

@pytest.mark.asyncio
@patch('illumidesk.apis.jupyterhub_api.JupyterHubAPI._request')
async def test_create_group_uses_request_helper_method_with_correct_values(mock_request, jupyterhub_api_environ):
    """
    Does create_group method use the helper method and pass the correct values?
    """
    sut = JupyterHubAPI()
    await sut.create_group('some-value')
    assert mock_request.called
    mock_request.assert_called_with('groups/some-value', body='', method='POST')

@pytest.mark.asyncio
@patch('illumidesk.apis.jupyterhub_api.JupyterHubAPI._request')
async def test_get_group_uses_request_helper_method_with_correct_values(mock_request, jupyterhub_api_environ):
    """
    Does get_group method use the helper method and pass the correct values?
    """
    sut = JupyterHubAPI()
    await sut.get_group('some-value')
    assert mock_request.called
    mock_request.assert_called_with('groups/some-value')

@pytest.mark.asyncio
@patch('illumidesk.apis.jupyterhub_api.JupyterHubAPI._request')
async def test_create_users_uses_request_helper_method_with_correct_values(mock_request, jupyterhub_api_environ):
    """
    Does get_group method use the helper method and pass the correct values?
    """
    sut = JupyterHubAPI()
    await sut.create_users('new_user')
    assert mock_request.called
    body_usernames ={
        'usernames': ['new_user']
    }
    mock_request.assert_called_with('users', method='POST', body=json.dumps(body_usernames))
