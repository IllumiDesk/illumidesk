import pytest
from illumidesk.spawners.hooks import custom_auth_state_hook
from illumidesk.spawners.spawners import IllumiDeskRoleDockerSpawner


@pytest.mark.asyncio
async def test_ensure_environment_assigned_to_user_role_from_auth_state_in_spawner_environment(auth_state_dict):
    """
    Does the user's docker container environment reflect his/her role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    custom_auth_state_hook(sut, auth_state_dict['auth_state'])
    # make sure the hook set the environment variables
    assert sut.environment['USER_ROLE'] == 'Learner'


@pytest.mark.asyncio
async def test_ensure_environment_assigned_to_workspace_type_from_auth_state_in_spawner_environment(auth_state_dict):
    """
    Does the user's docker container environment reflect his/her role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    custom_auth_state_hook(sut, auth_state_dict['auth_state'])
    # make sure the hook set the environment variables
    assert sut.environment['USER_WORKSPACE_TYPE'] == 'notebook'


@pytest.mark.asyncio
async def test_auth_state_hook_does_not_raise_an_error_if_workspace_type_is_missing(auth_state_dict):
    """
    Does the user's docker container environment reflect his/her role?
    """
    sut = IllumiDeskRoleDockerSpawner()
    # remove the workspace_type key from auth_state
    del auth_state_dict['auth_state']['workspace_type']
    custom_auth_state_hook(sut, auth_state_dict['auth_state'])
    # make sure the hook set the environment
    assert sut.environment
    assert 'USER_WORKSPACE_TYPE' not in sut.environment
