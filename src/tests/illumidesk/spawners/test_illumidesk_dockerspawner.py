import os
import pytest
import types

from dockerspawner.dockerspawner import DockerSpawner

from illumidesk.spawners.spawners import IllumiDeskRoleDockerSpawner
from illumidesk.spawners.spawners import IllumiDeskWorkSpaceDockerSpawner


def test_get_image_name_returns_standard_image_with_empty_role_in_user_environment(
    monkeypatch, setup_image_environ, mock_user
):
    """
    Does the internal image_from_role method accept and empty/none value?
    """
    sut = IllumiDeskRoleDockerSpawner()
    attrs = {'name': 'foo', 'environment': {'USER_ROLE': ''}}
    mock_user.configure_mock(**attrs)
    sut.user = mock_user

    assert sut._get_image_name() == os.environ.get('DOCKER_LEARNER_IMAGE')


@pytest.mark.asyncio
async def test_get_image_name_uses_default_image_with_unrecognized_role_in_user_environment(
    monkeypatch, setup_image_environ, mock_user
):
    """
    Does the internal image_from_role method return our standard image with an unrecognized role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    attrs = {'name': 'foo', 'environment': {'USER_ROLE': 'fake'}}
    mock_user.configure_mock(**attrs)
    sut.user = mock_user

    assert sut._get_image_name() == os.environ.get('DOCKER_STANDARD_IMAGE')


def test_get_image_name_uses_correct_image_with_student_role_in_user_environment(
    monkeypatch, setup_image_environ, mock_user
):
    """
    Does the internal image_from_role method accept and empty/none value?
    """
    sut = IllumiDeskRoleDockerSpawner()
    attrs = {'name': 'foo', 'environment': {'USER_ROLE': 'Student'}}
    mock_user.configure_mock(**attrs)
    sut.user = mock_user

    assert sut._get_image_name() == os.environ.get('DOCKER_LEARNER_IMAGE')


def test_get_image_name_uses_correct_image_with_learner_role_in_user_environment(
    monkeypatch, setup_image_environ, mock_user
):
    """
    Does the internal image_from_role method return student image when using the Student role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    attrs = {'name': 'foo', 'environment': {'USER_ROLE': 'Learner'}}
    mock_user.configure_mock(**attrs)
    sut.user = mock_user

    assert sut._get_image_name() == os.environ.get('DOCKER_LEARNER_IMAGE')


def test_get_image_name_uses_correct_image_with_instructor_role_in_user_environment(
    monkeypatch, setup_image_environ, mock_user
):
    """
    Does the internal image_from_role method return instructor image when using the Instructor role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    attrs = {'name': 'foo', 'environment': {'USER_ROLE': 'Instructor'}}
    mock_user.configure_mock(**attrs)
    sut.user = mock_user

    assert sut._get_image_name() == os.environ.get('DOCKER_INSTRUCTOR_IMAGE')


@pytest.mark.asyncio
async def test_ensure_environment_assigned_to_user_role_from_auth_state_in_user_environment(
    monkeypatch, auth_state_dict
):
    """
    Does the user's docker container environment reflect his/her role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    monkeypatch.setitem(auth_state_dict['auth_state'], 'user_role', 'Learner')

    await sut.auth_state_hook(auth_state_dict['auth_state'])
    assert sut.environment['USER_ROLE'] == 'Learner'


@pytest.mark.asyncio
async def test_get_image_name_uses_correct_image_for_rstudio_workspace_type(
    monkeypatch, auth_state_dict, mock_user, setup_image_environ
):
    """
    Does the user's docker container environment reflect the desired rstudio workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'rstudio')
    attrs = {'name': 'foo', 'environment': {'USER_WORKSPACE_TYPE': 'rstudio'}}
    mock_user.configure_mock(**attrs)
    sut.user = mock_user

    assert sut._get_image_name() == os.environ.get('DOCKER_RSTUDIO_IMAGE')


@pytest.mark.asyncio
async def test_get_image_name_uses_correct_image_for_theia_workspace_type(
    monkeypatch, auth_state_dict, mock_user, setup_image_environ
):
    """
    Does the user's docker container environment reflect the desired theia workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'theia')
    attrs = {'name': 'foo', 'environment': {'USER_WORKSPACE_TYPE': 'theia'}}
    mock_user.configure_mock(**attrs)
    sut.user = mock_user

    assert sut._get_image_name() == os.environ.get('DOCKER_THEIA_IMAGE')


@pytest.mark.asyncio
async def test_get_image_name_uses_correct_image_for_vscode_workspace_type(
    monkeypatch, auth_state_dict, mock_user, setup_image_environ
):
    """
    Does the user's docker container environment reflect the desired vscode workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'vscode')
    attrs = {'name': 'foo', 'environment': {'USER_WORKSPACE_TYPE': 'vscode'}}
    mock_user.configure_mock(**attrs)
    sut.user = mock_user

    assert sut._get_image_name() == os.environ.get('DOCKER_VSCODE_IMAGE')


@pytest.mark.asyncio
async def test_get_image_name_uses_correct_image_for_notebook_workspace_type(
    monkeypatch, auth_state_dict, mock_user, setup_image_environ
):
    """
    Does the user's docker container environment reflect the desired notebook workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'notebook')
    attrs = {'name': 'foo', 'environment': {'USER_WORKSPACE_TYPE': 'notebook'}}
    mock_user.configure_mock(**attrs)
    sut.user = mock_user

    assert sut._get_image_name() == os.environ.get('DOCKER_STANDARD_IMAGE')


def test_dockerspawner_uses_raw_username_in_format_volume_name():
    """
    Does the dockerspawner uses correctly the username?
    """
    d = DockerSpawner()
    # notice we're not using variable for username,
    # it helps understanding how volumes are binding
    d.user = types.SimpleNamespace(name='dbs__user5')
    d.volumes = {'data/{raw_username}': {'bind': '/home/{raw_username}'}}
    assert d.volume_binds == {'data/dbs__user5': {'bind': '/home/dbs__user5', 'mode': 'rw'}}
    assert d.volume_mount_points == ['/home/dbs__user5']
