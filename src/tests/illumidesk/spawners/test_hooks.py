from illumidesk.spawners.hooks import custom_auth_state_hook
from illumidesk.spawners.spawners import IllumiDeskDockerSpawner


def test_ensure_environment_assigned_to_user_role_from_auth_state_in_spawner_environment(auth_state_dict):
    """
    Does the user's docker container environment reflect his/her role?
    """
    sut = IllumiDeskDockerSpawner()
    custom_auth_state_hook(sut, auth_state_dict['auth_state'])
    # make sure the hook set the environment variables
    assert sut.environment['USER_ROLE'] == 'Learner'


def test_auth_state_hook_does_not_add_shared_folder_in_volumes_when_this_feature_is_disabled(
    auth_state_dict, monkeypatch
):
    """
    Does the auth_state_hook ignore the shared-folder when the SHARED_FOLDER_ENABLED is false or empty?
    """
    monkeypatch.setenv('SHARED_FOLDER_ENABLED', '')
    sut = IllumiDeskDockerSpawner()
    custom_auth_state_hook(sut, auth_state_dict['auth_state'])
    # make sure the hook set the environment variables
    assert 'shared' not in sut.volumes

    monkeypatch.setenv('SHARED_FOLDER_ENABLED', 'False')
    sut = IllumiDeskDockerSpawner()
    custom_auth_state_hook(sut, auth_state_dict['auth_state'])
    # make sure the hook set the environment variables
    assert len([v for v in sut.volumes if '/shared' in v]) == 0


def test_auth_state_hook_adds_shared_folder_in_volumes_when_the_feat_is_enabled(
    auth_state_dict, monkeypatch, tmp_path
):
    """
    Does the auth_state_hook add the shared-folder when the SHARED_FOLDER_ENABLED is True
    """
    monkeypatch.setenv('SHARED_FOLDER_ENABLED', 'true')
    monkeypatch.setenv('MNT_ROOT', str(tmp_path))
    monkeypatch.setenv('DOCKER_NOTEBOOK_DIR', '/home/jovyan')

    sut = IllumiDeskDockerSpawner()
    custom_auth_state_hook(sut, auth_state_dict['auth_state'])
    # make sure the hook set the environment variables
    assert len([v for v in sut.volumes if '/shared' in v]) > 0


def test_auth_state_hook_does_not_add_shared_folder_with_instructor(auth_state_dict, monkeypatch, tmp_path):
    """
    Does the auth_state_hook ignore the shared folder for instructors?
    """
    monkeypatch.setenv('SHARED_FOLDER_ENABLED', 'true')
    monkeypatch.setenv('MNT_ROOT', str(tmp_path))
    monkeypatch.setenv('DOCKER_NOTEBOOK_DIR', '/home/jovyan')

    sut = IllumiDeskDockerSpawner()
    auth_state_dict['auth_state']['user_role'] = 'Instructor'
    sut.load_shared_folder_with_instructor = False

    custom_auth_state_hook(sut, auth_state_dict['auth_state'])
    # make sure the hook set the environment variables
    assert len([v for v in sut.volumes if '/shared' in v]) == 0
