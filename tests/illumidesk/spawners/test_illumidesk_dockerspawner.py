import time
import os

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
