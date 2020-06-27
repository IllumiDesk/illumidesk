import os
import pytest
import types

from dockerspawner.dockerspawner import DockerSpawner

from illumidesk.spawners.spawners import IllumiDeskRoleDockerSpawner


@pytest.fixture(scope="function")
def setup_environ(monkeypatch):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('DOCKER_STANDARD_IMAGE', 'standard_image')
    monkeypatch.setenv('DOCKER_LEARNER_IMAGE', 'learner_image')
    monkeypatch.setenv('DOCKER_INSTRUCTOR_IMAGE', 'instructor_image')
    monkeypatch.setenv('DOCKER_GRADER_IMAGE', 'grader_image')


def test_image_from_key_raises_an_error_with_empty_user_role():
    """
    Does the internal image_from_role method accept and empty/none value?
    """
    sut = IllumiDeskRoleDockerSpawner()
    with pytest.raises(ValueError):
        sut._image_from_key('')


def test_image_from_key_uses_default_image_for_role_not_considered(setup_environ):
    """
    Does the internal image_from_role method return our standard image?
    """
    sut = IllumiDeskRoleDockerSpawner()
    result = sut._image_from_key('unknown')
    assert result == os.environ.get('DOCKER_STANDARD_IMAGE')


def test_image_from_key_uses_correct_image_for_STUDENT_role(setup_environ):
    """
    Does the internal image_from_role method return student image?
    """
    sut = IllumiDeskRoleDockerSpawner()
    # act
    image = sut._image_from_key('Student')
    assert image == os.environ.get('DOCKER_LEARNER_IMAGE')


def test_image_from_key_uses_correct_image_for_INSTRUCTOR_role(setup_environ):
    """
    Does the internal image_from_role method return instructor image?
    """
    sut = IllumiDeskRoleDockerSpawner()
    image = sut._image_from_key('Instructor')
    assert image == os.environ.get('DOCKER_INSTRUCTOR_IMAGE')


def test_image_from_key_uses_correct_image_for_GRADER_role(setup_environ):
    """
    Does the internal image_from_role method return grader image?
    """
    sut = IllumiDeskRoleDockerSpawner()
    image = sut._image_from_key('Grader')
    assert image == os.environ.get('DOCKER_GRADER_IMAGE')


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

    await test_spawner.auth_state_hook(None, authenticator_auth_state['auth_state'])

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
