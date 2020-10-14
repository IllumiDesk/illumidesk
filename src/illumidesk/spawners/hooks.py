import os
import shutil

from jupyterhub.spawner import Spawner

from illumidesk.authenticators.utils import user_is_an_instructor


def custom_auth_state_hook(spawner: Spawner, auth_state: dict) -> None:
    """
    Customized hook to:
    - set environment variables, for example the USER_ROLE from LTI user role.
    - obtain the course_id from auth_state to add the shared folder in the volumes list dynamically
    """
    if not auth_state:
        raise ValueError('auth_state not enabled.')
    spawner.log.debug('auth_state_hook set with %s role' % auth_state['user_role'])
    user_role = auth_state['user_role']
    # set spawner environment
    spawner.environment['USER_ROLE'] = user_role
    spawner.log.debug('Assigned USER_ROLE env var to %s' % spawner.environment['USER_ROLE'])
    # get the course-id from auth_state to add the shared folder only for this course
    course_id = auth_state['course_id']
    # Organization name
    org_name = os.environ.get('ORGANIZATION_NAME') or 'my-org'
    # Notebook directory within docker image
    notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR')
    # Root directory to mount org, home, and exchange folders
    mnt_root = os.environ.get('MNT_ROOT')
    # add the shared folder as a volume if it was enabled
    shared_folder_enabled = os.environ.get('SHARED_FOLDER_ENABLED') or 'False'
    # shared-folder feat is enabled but we make sure the instructor must have it
    shared_folder_allowed = (
        True if not user_is_an_instructor(user_role) else spawner.load_shared_folder_with_instructor
    )
    if shared_folder_enabled.lower() in ('true', '1') and course_id and shared_folder_allowed:
        spawner.log.debug('Adding the shared folder for %s' % course_id)
        spawner.volumes[f'{mnt_root}/{org_name}' + '/shared/' + course_id] = notebook_dir + '/shared'
        spawner.log.debug(f'Volumes to mount {spawner.volumes}')


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
            user_path,
            user=int(os.environ.get('NB_NON_GRADER_UID')),
            group=int(os.environ.get('NB_GID')),
        )
        os.chmod(user_path, 0o755)
