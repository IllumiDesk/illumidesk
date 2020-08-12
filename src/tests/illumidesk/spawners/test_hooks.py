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
