import types

from dockerspawner.dockerspawner import DockerSpawner


def test_dockerspawner_uses_raw_username_in_format_volume_name():
    """
    Does the correctly use the username?
    """
    d = DockerSpawner()
    # notice we're not using variable for username,
    # it helps understanding how volumes are binding
    d.user = types.SimpleNamespace(name='dbs__user5')
    d.volumes = {'data/{raw_username}': {'bind': '/home/{raw_username}'}}
    assert d.volume_binds == {'data/dbs__user5': {'bind': '/home/dbs__user5', 'mode': 'rw'}}
    assert d.volume_mount_points == ['/home/dbs__user5']
