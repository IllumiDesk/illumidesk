import os
import pytest
import types

from dockerspawner.dockerspawner import DockerSpawner

from illumidesk.spawners.spawners import IllumiDeskRoleDockerSpawner
from illumidesk.spawners.spawners import IllumiDeskWorkSpaceDockerSpawner


def test_image_from_key_raises_a_value_error_error_with_empty_user_role():
    """
    Does the internal image_from_role method accept and empty/none value?
    """
    sut = IllumiDeskRoleDockerSpawner()
    with pytest.raises(ValueError):
        sut._image_from_key('')


def test_image_from_key_raises_a_value_error_error_with_empty_workspace():
    """
    Does the internal image_from_role method accept and empty/none value?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    with pytest.raises(ValueError):
        sut._image_from_key('')


@pytest.mark.asyncio
async def test_ensure_environment_assigned_to_user_role_from_auth_state():
    """
    Does the user's docker container environment reflect his/her role?
    """
    test_spawner = IllumiDeskRoleDockerSpawner()

    authenticator_auth_state = {
        'name': 'username',
        'auth_state': {
            'course_id': 'intro101',
            'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
            'user_role': 'Learner',
            'workspace_type': 'notebook',
        },
    }

    await test_spawner.auth_state_hook(authenticator_auth_state['auth_state'])
    assert test_spawner.environment['USER_ROLE'] == 'Learner'


def test_dockerspawner_uses_raw_username_in_format_volume_name():
    """
    Does the dockerspawner uses correctly the username?
    """
    d = DockerSpawner()
    # notice we're not using variable for username,
    # it helps understanding how volumes are binding
    d.user = types.SimpleNamespace(name="dbs__user5")
    d.volumes = {"data/{raw_username}": {"bind": "/home/{raw_username}"}}
    assert d.volume_binds == {"data/dbs__user5": {"bind": "/home/dbs__user5", "mode": "rw"}}
    assert d.volume_mount_points == ["/home/dbs__user5"]


@pytest.mark.asyncio
async def test_ensure_environment_assigned_to_workspace_from_auth_state():
    """
    Does the user's docker container environment reflect the desired workspace?
    """
    test_spawner = IllumiDeskWorkSpaceDockerSpawner()

    authenticator_auth_state = {
        'name': 'username',
        'auth_state': {
            'course_id': 'intro101',
            'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
            'user_role': 'Learner',
            'workspace_type': 'notebook',
        },
    }

    await test_spawner.auth_state_hook(authenticator_auth_state['auth_state'])
    assert test_spawner.environment['USER_WORKSPACE_TYPE'] == 'notebook'


def test_image_from_key_uses_default_image_for_role_not_considered(setup_image_environ):
    """
    Does the internal image_from_role method return our standard image?
    """
    sut = IllumiDeskRoleDockerSpawner()
    result = sut._image_from_key('unknown')
    assert result == os.environ.get('DOCKER_STANDARD_IMAGE')


def test_image_from_key_uses_correct_image_for_student_role(setup_image_environ):
    """
    Does the internal image_from_role method return student image when using the Student role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    sut.image = sut._image_from_key('Student')
    assert sut.image == os.environ.get('DOCKER_LEARNER_IMAGE')


def test_image_from_key_uses_correct_image_for_learner_role(setup_image_environ):
    """
    Does the internal image_from_role method return student image when using the Learner role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    sut.image = sut._image_from_key('Learner')
    assert sut.image == os.environ.get('DOCKER_LEARNER_IMAGE')


def test_image_from_key_uses_correct_image_for_instructor_role(setup_image_environ):
    """
    Does the internal image_from_role method return instructor image when using the Instructor role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    sut.image = sut._image_from_key('Instructor')
    assert sut.image == os.environ.get('DOCKER_INSTRUCTOR_IMAGE')


def test_image_from_key_uses_correct_image_for_grader_role(setup_image_environ):
    """
    Does the internal image_from_role method return grader image when using the Grader role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    sut.image = sut._image_from_key('Grader')
    assert sut.image == os.environ.get('DOCKER_GRADER_IMAGE')


@pytest.mark.asyncio
async def test_image_from_key_uses_correct_image_for_rstudio_workspace_type(setup_image_environ):
    """
    Does the user's docker container environment reflect the desired rstudio workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()

    authenticator_auth_state = {
        'name': 'username',
        'auth_state': {
            'course_id': 'intro101',
            'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
            'user_role': 'Learner',
            'workspace_type': 'rstudio',
        },
    }

    await sut.auth_state_hook(authenticator_auth_state['auth_state'])
    assert sut.environment['USER_WORKSPACE_TYPE'] == 'rstudio'
    assert sut.image == os.environ.get('DOCKER_RSTUDIO_IMAGE')


@pytest.mark.asyncio
async def test_image_from_key_uses_correct_image_for_theia_workspace_type(setup_image_environ):
    """
    Does the user's docker container environment reflect the desired theia workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()

    authenticator_auth_state = {
        'name': 'username',
        'auth_state': {
            'course_id': 'intro101',
            'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
            'user_role': 'Learner',
            'workspace_type': 'theia',
        },
    }

    await sut.auth_state_hook(authenticator_auth_state['auth_state'])
    assert sut.environment['USER_WORKSPACE_TYPE'] == 'theia'
    assert sut.image == os.environ.get('DOCKER_THEIA_IMAGE')


@pytest.mark.asyncio
async def test_image_from_key_uses_correct_image_for_vscode_workspace_type(setup_image_environ):
    """
    Does the user's docker container environment reflect the desired vscode workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()

    authenticator_auth_state = {
        'name': 'username',
        'auth_state': {
            'course_id': 'intro101',
            'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
            'user_role': 'Learner',
            'workspace_type': 'vscode',
        },
    }

    await sut.auth_state_hook(authenticator_auth_state['auth_state'])
    assert sut.environment['USER_WORKSPACE_TYPE'] == 'vscode'
    assert sut.image == os.environ.get('DOCKER_VSCODE_IMAGE')


@pytest.mark.asyncio
async def test_image_from_key_uses_correct_image_for_notebook_workspace_type(setup_image_environ):
    """
    Does the user's docker container environment reflect the desired vscode workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.image = sut._image_from_key('notebook')
    assert sut.image == os.environ.get('DOCKER_STANDARD_IMAGE')


@pytest.mark.asyncio
async def test_image_from_key_uses_correct_image_for_theia_workspace_type(setup_image_environ):
    """
    Does the user's docker container environment reflect the desired theia workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.image = sut._image_from_key('theia')
    assert sut.image == os.environ.get('DOCKER_THEIA_IMAGE')


@pytest.mark.asyncio
async def test_image_from_key_uses_correct_image_for_rstudio_workspace_type(setup_image_environ):
    """
    Does the user's docker container environment reflect the desired rstudio workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.image = sut._image_from_key('rstudio')
    assert sut.image == os.environ.get('DOCKER_RSTUDIO_IMAGE')


@pytest.mark.asyncio
async def test_image_from_key_uses_correct_image_for_vscode_workspace_type(setup_image_environ):
    """
    Does the user's docker container environment reflect the desired vscode workspace?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.image = sut._image_from_key('vscode')
    assert sut.image == os.environ.get('DOCKER_VSCODE_IMAGE')


@pytest.mark.asyncio
async def test_unrecognized_image_from_key_defaults_to_standard_workspace_type(setup_image_environ):
    """
    Does the user's docker container environment use the standard image when an unrecognized workspace
    type is sent?
    """
    sut = IllumiDeskWorkSpaceDockerSpawner()
    sut.image = sut._image_from_key('fake')
    assert sut.image == os.environ.get('DOCKER_STANDARD_IMAGE')
