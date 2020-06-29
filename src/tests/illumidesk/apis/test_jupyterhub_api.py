import json
import pytest
import os

from tornado.httpclient import AsyncHTTPClient

from unittest.mock import patch

from illumidesk.apis.jupyterhub_api import JupyterHubAPI


def test_initializer_raises_error_without_JUPYTERHUB_API_TOKEN_env(monkeypatch):
    """
    Does initializer raise an error when JUPYTERHUB_API_TOKEN was not set?
    """
    monkeypatch.delenv('JUPYTERHUB_API_TOKEN', raising=False)
    with pytest.raises(EnvironmentError):
        _ = JupyterHubAPI()


def test_initializer_raises_error_without_JUPYTERHUB_API_URL_env(monkeypatch):
    """
    Does initializer raise an error when 'JUPYTERHUB_API_URL' was not set?
    """
    monkeypatch.delenv('JUPYTERHUB_API_URL', raising=False)
    with pytest.raises(EnvironmentError):
        _ = JupyterHubAPI()


def test_initializer_sets_http_client(jupyterhub_api_environ):
    """
    Does initializer set a httpclient instance?
    """
    sut = JupyterHubAPI()
    assert sut.client is not None
    assert isinstance(sut.client, AsyncHTTPClient)


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
    Does create_users method use the helper method and pass the correct values?
    """
    sut = JupyterHubAPI()
    await sut.create_users('new_user')
    assert mock_request.called
    body_usernames = {'usernames': ['new_user']}
    mock_request.assert_called_with('users', method='POST', body=json.dumps(body_usernames))


@pytest.mark.asyncio
@patch('illumidesk.apis.jupyterhub_api.JupyterHubAPI._request')
async def test_create_user_uses_request_helper_method_with_correct_values(mock_request, jupyterhub_api_environ):
    """
    Does create_user method use the helper method and pass the correct values?
    """
    sut = JupyterHubAPI()
    await sut.create_user('new_user')
    assert mock_request.called
    body_usernames = {'usernames': ['new_user']}
    mock_request.assert_called_with('users/new_user', method='POST', body='')


@pytest.mark.asyncio
@patch('illumidesk.apis.jupyterhub_api.JupyterHubAPI._request')
async def test_add_group_member_uses_request_helper_method_with_correct_values(mock_request, jupyterhub_api_environ):
    """
    Does add_group_member method use the helper method and pass the correct values?
    """
    sut = JupyterHubAPI()
    await sut.add_group_member('to_group', 'a_user')
    assert mock_request.called
    body_usernames = {'users': ['a_user']}
    mock_request.assert_called_with('groups/to_group/users', method='POST', body=json.dumps(body_usernames))


def test_jupyterhub_api_url_with_empty_base_url_env(jupyterhub_api_environ):
    """
    Does initializer correctly set the 'JUPYTERHUB_API_URL' when the JUPYTERHUB_BASE_URL has an
    empty string as a value?
    """
    expected = 'https://localhost/hub/api'
    sut = JupyterHubAPI()
    actual = sut.api_root_url
    assert expected == actual


def test_jupyterhub_api_url_with_base_url_env(jupyterhub_api_with_custom_base_environ):
    """
    Does initializer correctly set the 'JUPYTERHUB_API_URL' when using the JUPYTERHUB_BASE_URL?
    """
    expected = 'https://localhost/acme/hub/api'
    sut = JupyterHubAPI()
    actual = sut.api_root_url
    assert expected == actual
