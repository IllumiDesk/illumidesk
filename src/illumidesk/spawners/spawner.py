import os
import shutil
import time

from dockerspawner import DockerSpawner


class IllumiDeskDockerSpawner(DockerSpawner):
    """
    Custom DockerSpawner which assigns a user notebook image
    based on the user's role. This spawner requires:

    1. That the `Authenticator.enable_auth_state = True`
    2. That the user's `USER_ROLE` environment variable is set
    """

    def _image_from_role(self, user_role: str) -> str:
        """
        Given a user role, return the right image
        Args:
            user_role: the user's role
        Returns:
            docker_image: docker image used to spawn container based on role
        """
        if not user_role:
            raise ValueError('user_role is missing')
        # default to standard image, otherwise assign image based on role
        self.log.debug('User role used to set image: %s' % user_role)
        docker_image = str(os.environ.get('DOCKER_STANDARD_IMAGE'))
        if user_role == 'Learner' or user_role == 'Student':
            docker_image = str(os.environ.get('DOCKER_LEARNER_IMAGE'))
        elif user_role == 'Instructor':
            docker_image = str(os.environ.get('DOCKER_INSTRUCTOR_IMAGE'))
        elif user_role == 'Grader':
            docker_image = str(os.environ.get('DOCKER_GRADER_IMAGE'))
        self.log.debug('Image based on user role set to %s' % docker_image)
        return docker_image

    async def auth_state_hook(self, spawner, auth_state):
        """
        Customized hook to assign USER_ROLE environment variable to LTI user role.
        The USER_ROLE environment variable is used to select the notebook image based
        on the user's role.
        """
        if not auth_state:
            self.log.debug('auth_state not enabled.')
            return
        self.log.debug('auth_state_hook set with %s role' % auth_state['user_role'])
        self.environment['USER_ROLE'] = auth_state['user_role']
        self.log.debug('Assigned USER_ROLE env var to %s' % self.environment['USER_ROLE'])

    # Create a new user directory if it does not exist on the host, regardless
    # of whether or not its mounted with NFS.
    def pre_spawn_hook(self, spawner):
        """
        Creates the user directory based on information passed from the
        `spawner` object.

        Args:
            spawner: JupyterHub spawner object
        """
        if not self.user.name:
            raise ValueError('Spawner object does not contain the username')
        username = self.user.name
        user_path = os.path.join('/home', username)
        if not os.path.exists(user_path):
            os.mkdir(user_path)
            shutil.chown(
                user_path, user=int(os.environ.get('MNT_HOME_DIR_UID')), group=int(os.environ.get('MNT_HOME_DIR_GID')),
            )
            os.chmod(user_path, 0o755)
        time.sleep(5)

    def start(self):
        user_role = self.user.spawner.environment.get('USER_ROLE') or 'Learner'
        self.log.debug('User %s has role: %s' % (self.user.name, user_role))
        self.image = self._image_from_role(str(user_role))
        self.log.debug('Starting with image: %s' % self.image)
        return super().start()
