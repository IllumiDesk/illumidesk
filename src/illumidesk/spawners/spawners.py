import os
import shutil

from dockerspawner import DockerSpawner


class IllumiDeskBaseDockerSpawner(DockerSpawner):
    """
    Custom base DockerSpawner which provides the option to designate the image to
    spawn based on values set within the authentication dictionary's ``auth_state``, ``nested-key``,
    where the ``nested-key`` has a key name of your choosing.

    For example, if you would like to spawn an image based on the nested key's value
    ``foo`` the authenticator should return a dictionary with ``authentication['auth_state']['foo']``.
    This base class requires that ``Authenticator.enable_auth_state = True.``
    """

    def _get_image_name(self) -> str:
        """
        Return the image to spawn based on the given the auth_state key/value.
        
        Returns:
            docker_image: docker image used to spawn a container.
        """
        raise NotImplementedError

    async def auth_state_hook(self, auth_state: dict) -> dict:
        """
        Customized hook to assign an environment variable based on a value provided
        by the authentication's auth_state dictionary.
        """
        if not auth_state:
            self.log.debug('auth_state not enabled.')
            return
        self.log.debug('auth_state_hook using auth_state %s' % auth_state)
        self.environment['USER_ROLE'] = auth_state['user_role']
        self.log.debug('Assigned USER_ROLE env var to %s' % self.environment['USER_ROLE'])
        self.environment['USER_WORKSPACE_TYPE'] = auth_state['workspace_type']
        self.log.debug('Assigned USER_WORKSPACE_TYPE env var to %s' % self.environment['USER_WORKSPACE_TYPE'])

    def pre_spawn_hook(self) -> None:
        """
        Creates the user directory based on information passed from the
        ``spawner`` object. This setup assumes that users and groups aren't added
        with the container's operating system so we need to create directories and
        set the appropriate permissions.

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

    def start(self):
        """
        Start the user's server by setting the image and based on the spawner's environment
        using the auth_state_hook to set the user's image based on a key/value within the auth_state
        dictionary.

        To run/start the server user the super class's run function, i.e. ``return super().start()``.
        """
        self.image = self._get_image_name()
        return super().start()


class IllumiDeskRoleDockerSpawner(IllumiDeskBaseDockerSpawner):
    """
    Custom DockerSpawner which assigns a user notebook image
    based on the user's role. This spawner requires:

    1. That the `Authenticator.enable_auth_state = True`
    2. That the user's `USER_ROLE` environment variable is set
    """

    def _get_image_name(self) -> str:
        """
        Given a user role, return the required image base on role.

        Returns:
            docker_image: docker image used to spawn container based on role
        """
        user_role = self.user.environment.get('USER_ROLE') or 'Learner'
        self.log.debug('User %s has role: %s' % (self.user.name, user_role))
        # default to standard image, otherwise assign image based on role
        self.log.debug('User role used to set image: %s' % user_role)
        docker_image = str(os.environ.get('DOCKER_STANDARD_IMAGE'))
        if user_role == 'Learner' or user_role == 'Student':
            docker_image = str(os.environ.get('DOCKER_LEARNER_IMAGE'))
        elif user_role == 'Instructor':
            docker_image = str(os.environ.get('DOCKER_INSTRUCTOR_IMAGE'))
        self.log.debug('Image based on user role set to %s' % docker_image)
        return docker_image


class IllumiDeskWorkSpaceDockerSpawner(IllumiDeskBaseDockerSpawner):
    """
    Custom DockerSpawner which assigns a user notebook image
    based on the ``workspace_type`` value in the query parameter.
    
    This spawner requires that ``Authenticator.enable_auth_state = True``

    If the ``workspace`` parameter is not set, then the image
    defaults value provided by the DOCKER_STANDARD_IMAGE env var.
    """

    def _get_image_name(self) -> str:
        """
        Given a workspace type, return the right image.

        Returns:
            docker_image: docker image based on the desired workspace_type
        """
        workspace_type = self.user.environment.get('USER_WORKSPACE_TYPE') or 'notebook'
        self.log.debug('User %s has workspace type set to: %s' % (self.user.name, workspace_type))
        docker_image = os.environ.get('DOCKER_STANDARD_IMAGE')
        if workspace_type == 'theia':
            docker_image = os.environ.get('DOCKER_THEIA_IMAGE')
        elif workspace_type == 'rstudio':
            docker_image = os.environ.get('DOCKER_RSTUDIO_IMAGE')
        elif workspace_type == 'vscode':
            docker_image = os.environ.get('DOCKER_VSCODE_IMAGE')
        self.log.debug('Image based on workspace type set to %s' % docker_image)
        return docker_image
