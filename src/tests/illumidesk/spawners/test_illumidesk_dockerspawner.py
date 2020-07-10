import os
import pytest
import types

from dockerspawner.dockerspawner import DockerSpawner

from illumidesk.spawners.spawners import IllumiDeskRoleDockerSpawner
from illumidesk.spawners.spawners import IllumiDeskWorkSpaceDockerSpawner


def test_get_image_name_returns_correct_image_for_student_role(setup_image_environ, mock_jhub_user):
    """
    Does the internal get_image_name method return the correct image with the student role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    sut.environment['USER_ROLE'] = 'Student'
    sut.user = mock_jhub_user()

    assert sut._get_image_name() == os.environ.get('DOCKER_LEARNER_IMAGE')


def test_get_image_name_returns_correct_image_for_learner_role(setup_image_environ, mock_jhub_user):
    """
    Does the internal get_image_name method return student image when using the learner role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    sut.environment['USER_ROLE'] = 'Learner'
    sut.user = mock_jhub_user()

    assert sut._get_image_name() == os.environ.get('DOCKER_LEARNER_IMAGE')


def test_get_image_name_returns_correct_image_for_Instructor_role(setup_image_environ, mock_jhub_user):
    """
    Does the internal get_image_name method return instructor image when using the Instructor role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    sut.environment['USER_ROLE'] = 'Instructor'
    sut.user = mock_jhub_user()

    assert sut._get_image_name() == os.environ.get('DOCKER_INSTRUCTOR_IMAGE')


def test_get_image_name_returns_Standard_image_for_unknown_role(setup_image_environ, mock_jhub_user):
    """
    Does the internal get_image_name method return Standard image when using an unknown role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    sut.environment['USER_ROLE'] = 'any-value'
    sut.user = mock_jhub_user()

    assert sut._get_image_name() == os.environ.get('DOCKER_STANDARD_IMAGE')


@pytest.mark.asyncio
async def test_get_image_name_returns_correct_image_for_rstudio_workspace_type(
    auth_state_dict, mock_jhub_user, setup_image_environ
):
    """
    Does the user's docker container environment reflect the rstudio workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.user = mock_jhub_user()
    auth_state_dict['auth_state']['workspace_type'] = 'rstudio'
    # call our hook to set the environment in the spawner and pass into it the auth_state
    await sut.run_auth_state_hook(auth_state_dict['auth_state'])

    assert sut._get_image_name() == os.environ.get('DOCKER_RSTUDIO_IMAGE')


@pytest.mark.asyncio
async def test_get_image_name_returns_correct_image_for_theia_workspace_type(
    auth_state_dict, mock_jhub_user, setup_image_environ
):
    """
    Does the user's docker container environment reflect the theia workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.user = mock_jhub_user()
    auth_state_dict['auth_state']['workspace_type'] = 'theia'
    # call our hook to set the environment in the spawner and pass into it the auth_state
    await sut.run_auth_state_hook(auth_state_dict['auth_state'])
    assert sut._get_image_name() == os.environ.get('DOCKER_THEIA_IMAGE')


@pytest.mark.asyncio
async def test_get_image_name_returns_correct_image_for_vscode_workspace_type(
    auth_state_dict, mock_jhub_user, setup_image_environ
):
    """
    Does the user's docker container environment reflect the vscode workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.user = mock_jhub_user()
    auth_state_dict['auth_state']['workspace_type'] = 'vscode'
    # call our hook to set the environment in the spawner and pass into it the auth_state
    await sut.run_auth_state_hook(auth_state_dict['auth_state'])

    assert sut._get_image_name() == os.environ.get('DOCKER_VSCODE_IMAGE')


@pytest.mark.asyncio
async def test_get_image_name_returns_correct_image_for_notebook_workspace_type(
    auth_state_dict, mock_jhub_user, setup_image_environ
):
    """
    Does the user's docker container environment reflect the notebook workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.user = mock_jhub_user()
    auth_state_dict['auth_state']['workspace_type'] = 'notebook'
    # call our hook to set the environment in the spawner and pass into it the auth_state
    await sut.run_auth_state_hook(auth_state_dict['auth_state'])

    assert sut._get_image_name() == os.environ.get('DOCKER_STANDARD_IMAGE')


@pytest.mark.asyncio
async def test_get_image_name_returns_default_image_for_empty_workspace_type(
    auth_state_dict, mock_jhub_user, setup_image_environ
):
    """
    Does the user's docker container environment reflect the notebook workspace when
    it's set to empty?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.user = mock_jhub_user()
    # remove the `workspace_type` key
    del auth_state_dict['auth_state']['workspace_type']
    # call our hook to set the environment in the spawner and pass into it the auth_state
    await sut.run_auth_state_hook(auth_state_dict['auth_state'])

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
