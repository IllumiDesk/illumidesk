import types

from dockerspawner.dockerspawner import DockerSpawner

from illumidesk.spawners.spawners import IllumiDeskDockerSpawner


def test_base_spawner_does_not_consider_shared_folder_with_instructor_role_when_jhub_setting_is_False(
    setup_image_environ, mock_jhub_user
):
    """
    Does the IllumiDeskDockerSpawner class exclude the shared folder for instructors when load_shared_folder_with_instructor is False?
    """
    sut = IllumiDeskDockerSpawner(load_shared_folder_with_instructor=False)
    sut.environment['USER_ROLE'] = 'Instructor'
    sut.user = mock_jhub_user()
    volumes_to_mount = {'mnt_root/my-org/shared/': 'home/jovyan/shared'}
    binds = sut._volumes_to_bind(volumes=volumes_to_mount, binds={})
    assert len(binds) == 0


def test_base_spawner_load_shared_folder_with_instructor_role_when_jhub_setting_is_True(
    setup_image_environ, mock_jhub_user
):
    """
    Does the IllumiDeskDockerSpawner class load the shared folder for instructors?
    """
    sut = IllumiDeskDockerSpawner(load_shared_folder_with_instructor=True)
    sut.environment['USER_ROLE'] = 'Instructor'
    sut.user = mock_jhub_user()
    volumes_to_mount = {'mnt_root/my-org/shared/': 'home/jovyan/shared'}
    binds = sut._volumes_to_bind(volumes=volumes_to_mount, binds={})
    assert len(binds) == 1


def test_base_spawner_returns_the_shared_folder_with_learner_role_not_matter_the_jhub_setting(
    setup_image_environ, mock_jhub_user
):
    """
    Does the IllumiDeskDockerSpawner class consider the shared folder for learners?
    """
    sut = IllumiDeskDockerSpawner()
    sut.environment['USER_ROLE'] = 'Learner'
    sut.user = mock_jhub_user()
    volumes_to_mount = {'mnt_root/my-org/shared/': 'home/jovyan/shared'}
    binds = sut._volumes_to_bind(volumes=volumes_to_mount, binds={})
    # First case (setting is not used)
    assert len(binds) == 1
    sut.load_shared_folder_with_instructor = False
    volumes_to_mount = {'mnt_root/my-org/shared/': 'home/jovyan/shared'}
    binds = sut._volumes_to_bind(volumes=volumes_to_mount, binds={})
    # First case (setting is used)
    assert len(binds) == 1


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
