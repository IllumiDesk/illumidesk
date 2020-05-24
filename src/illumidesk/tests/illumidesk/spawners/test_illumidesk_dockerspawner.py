import pytest

from illumidesk.spawners.spawner import IllumiDeskDockerSpawner


@pytest.mark.asyncio
async def ensure_environment_assigned_to_user_role_from_auth_state():
    """
    Does the user's docker container environment reflect his/her role?
    """
    test_spawner = IllumiDeskDockerSpawner()

    auth_state = {
        'name': 'username',
        'auth_state': {
            'course_id': 'intro101',
            'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
            'user_role': 'Learner',
        },
    }

    await test_spawner.auth_state_hook(auth_state)

    assert test_spawner.environment['USER_ROLE'] == 'Learner'


def test_dockerspawner_uses_raw_username_in_format_volume_name():
    import types
    from dockerspawner.dockerspawner import DockerSpawner

    d = DockerSpawner()
    # notice we're not using variable for username, 
    # it helps understanding how volumes are binding
    d.user = types.SimpleNamespace(name="dbs__user5")
    d.volumes = {"data/{raw_username}": {"bind": "/home/{raw_username}"}}
    assert (
        d.volume_binds
        == {"data/dbs__user5": {"bind": "/home/dbs__user5", "mode": "rw"}}
    )
    assert d.volume_mount_points == ["/home/dbs__user5"]
