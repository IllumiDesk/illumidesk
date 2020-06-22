import json
import pytest
import os

from unittest.mock import patch

from illumidesk.apis.jupyterhub_api import JupyterHubAPI


def test_initializer_raises_error_with_jupyterhub_api_token_env_as_missing(monkeypatch, jupyterhub_api_environ):
    """
    Does initializer raise an error when 'JUPYTERHUB_API_TOKEN' is an empty string?
    """
    monkeypatch.setenv('JUPYTERHUB_API_TOKEN', '')
    with pytest.raises(EnvironmentError):
        JupyterHubAPI()


def test_initializer_raises_error_with_jupyterhub_api_url_env_as_missing(monkeypatch, jupyterhub_api_environ):
    """
    Does initializer raise an error when 'JUPYTERHUB_API_URL' is an empty None?
    """
    monkeypatch.setenv('JUPYTERHUB_API_URL', '')
    with pytest.raises(EnvironmentError):
        JupyterHubAPI()


def test_initializer_sets_http_client(jupyterhub_api_environ):
    """
    Does initializer set a httpclient instance?
    """
    sut = JupyterHubAPI()
    assert sut.client is not None
    assert sut.client != ''


def test_initializer_sets_api_token_from_env_var(jupyterhub_api_environ):
    """
    Does initializer set the api token correctly?
    """
    sut = JupyterHubAPI()
    assert sut.token == os.environ.get('JUPYTERHUB_API_TOKEN')


def test_initializer_sets_api_url_from_env_var(jupyterhub_api_environ):
    """
    Does initializer set the api url correctly?
    """
    sut = JupyterHubAPI()
    assert sut.api_root_url == os.environ.get('JUPYTERHUB_API_URL')


def test_initializer_sets_headers_to_make_request(jupyterhub_api_environ):
    """
    Does initializer set the api url?
    """
    sut = JupyterHubAPI()
    assert sut.default_headers is not None
    assert type(sut.default_headers) is dict
    assert sut.default_headers['Authorization'] == f'token {os.environ.get("JUPYTERHUB_API_TOKEN")}'


@pytest.mark.asyncio
async def test_request_raises_value_error_with_endpoint_empty(jupyterhub_api_environ):
    """
    Does the _request method accespt an missing endpoint argument?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI()._request(endpoint='')


def test_request_builds_correct_url_variable(jupyterhub_api_environ):
    """
    Does the _request build the correct url based on the api url attribute and the
    endpoint argument?
    """
    endpoint = 'users'
    api_root_url = 'https://localhost/hub/api'
    actual = f'{api_root_url}/{endpoint}'
    expected = 'https://localhost/hub/api/users'
    assert expected == actual


@pytest.mark.asyncio
async def test_create_group_raises_error_with_group_empty(jupyterhub_api_environ):
    """
    Does create_group method accept a group_name empty?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().create_group('')


@pytest.mark.asyncio
async def test_get_group_raises_error_with_group_empty(jupyterhub_api_environ):
    """
    Does get_group method accept a group_name empty?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().get_group('')


@pytest.mark.asyncio
async def test_create_users_raises_error_with_users_empty(jupyterhub_api_environ):
    """
    Does create_users method accept an empty list of users?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().create_users()


@pytest.mark.asyncio
async def test_create_user_raises_error_with_users_empty(jupyterhub_api_environ):
    """
    Does create_user method accept an empty user?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().create_user(username='')


@pytest.mark.asyncio
async def test_add_group_member_raises_error_when_empty(jupyterhub_api_environ):
    """
    Does add_group_member method accept an empty user or an empty group name?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().add_group_member(username='', group_name='')

    with pytest.raises(ValueError):
        await JupyterHubAPI().add_group_member(username='foo', group_name='')

    with pytest.raises(ValueError):
        await JupyterHubAPI().add_group_member(username='', group_name='foo')


@pytest.mark.asyncio
async def test_add_user_to_nbgrader_gradebook_raises_error_when_empty(jupyterhub_api_environ):
    """
    Does add_user_to_nbgrader_gradebook method accept an empty course id, username, or lms user id?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().add_user_to_nbgrader_gradebook(course_id='', username='foo', lms_user_id='abc123')

    with pytest.raises(ValueError):
        await JupyterHubAPI().add_user_to_nbgrader_gradebook(course_id='abc', username='', lms_user_id='abc123')


@pytest.mark.asyncio
async def test_add_student_to_jupyterhub_group_raises_error_when_empty(jupyterhub_api_environ):
    """
    Does add_student_to_jupyterhub_group method accept an empty course id or student name?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().add_student_to_jupyterhub_group(course_id='', student='foo')

    with pytest.raises(ValueError):
        await JupyterHubAPI().add_student_to_jupyterhub_group(course_id='abc', student='')


@pytest.mark.asyncio
async def test_add_instructor_to_jupyterhub_group_raises_error_when_empty(jupyterhub_api_environ):
    """
    Does add_instructor_to_jupyterhub_group method accept an empty course id or instructor name?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().add_instructor_to_jupyterhub_group(course_id='', instructor='foo')

    with pytest.raises(ValueError):
        await JupyterHubAPI().add_instructor_to_jupyterhub_group(course_id='abc', instructor='')


@pytest.mark.asyncio
async def test_add_user_to_jupyterhub_group_raises_error_when_empty(jupyterhub_api_environ):
    """
    Does _add_user_to_jupyterhub_group method accept an empty username or course name?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI()._add_user_to_jupyterhub_group(username='', group_name='foo')

    with pytest.raises(ValueError):
        await JupyterHubAPI()._add_user_to_jupyterhub_group(username='abc', group_name='')


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
