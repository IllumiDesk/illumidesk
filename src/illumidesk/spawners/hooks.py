import os
import shutil

from jupyterhub.spawner import Spawner


def custom_auth_state_hook(spawner: Spawner, auth_state: dict) -> None:
    """
    Customized hook to assign USER_ROLE environment variable to LTI user role.
    The USER_ROLE environment variable is used to select the notebook image based
    on the user's role.
    """
    if not auth_state:
        raise ValueError('auth_state not enabled.')
    spawner.log.debug('auth_state_hook set with %s role' % auth_state['user_role'])
    spawner.environment['USER_ROLE'] = auth_state['user_role']
    spawner.log.debug('Assigned USER_ROLE env var to %s' % spawner.environment['USER_ROLE'])


def custom_pre_spawn_hook(spawner: Spawner) -> None:
    """
    Creates the user directory based on information passed from the
    `spawner` object.
    Args:
        spawner: JupyterHub spawner object
    """
    if not spawner.user.name:
        raise ValueError('Spawner object does not contain the username')
    username = spawner.user.name
    user_path = os.path.join('/home', username)
    if not os.path.exists(user_path):
        spawner.log.debug(f'Creating workdir {user_path} for the user {username}')
        os.mkdir(user_path)
        shutil.chown(
            user_path, user=int(os.environ.get('MNT_HOME_DIR_UID')), group=int(os.environ.get('MNT_HOME_DIR_GID')),
        )
        os.chmod(user_path, 0o755)
