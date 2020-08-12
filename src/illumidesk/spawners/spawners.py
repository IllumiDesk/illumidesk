import os

from dockerspawner import DockerSpawner

from illumidesk.authenticators.utils import user_is_a_student

from illumidesk.spawners.hooks import custom_auth_state_hook
from illumidesk.spawners.hooks import custom_pre_spawn_hook


class IllumiDeskBaseDockerSpawner(DockerSpawner):
    """
    Extends the DockerSpawner by defining the common behavior for our Spwaners that work with LTI versions 1.1 and 1.3
    """

    def _get_image_name(self) -> str:
        raise NotImplementedError(
            'It is necessary to implement the logic to indicate how to get the image name based on auth_state or environ in this child class'
        )

    def auth_state_hook(self, spawner: DockerSpawner, auth_state: dict) -> None:
        # call our custom hook from here without issue related with 'invalid arguments number given'
        custom_auth_state_hook(spawner, auth_state)

    def pre_spawn_hook(self, spawner) -> None:
        custom_pre_spawn_hook(spawner)

    def start(self) -> None:
        self.image = self._get_image_name()
        self.log.debug('Starting with image: %s' % self.image)
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
        Given a user role in the environ, return the right image
        Returns:
            docker_image: docker image used to spawn container based on role
        """
        user_role = self.environment.get('USER_ROLE') or 'Learner'
        self.log.debug('User %s has role: %s' % (self.user.name, user_role))

        # default to standard image, otherwise assign image based on role
        self.log.debug('User role used to set image: %s' % user_role)
        docker_image = str(os.environ.get('DOCKER_STANDARD_IMAGE'))
        if user_is_a_student(user_role):
            docker_image = str(os.environ.get('DOCKER_LEARNER_IMAGE'))
        elif user_role == 'Instructor':
            docker_image = str(os.environ.get('DOCKER_INSTRUCTOR_IMAGE'))
        elif user_role == 'Grader':
            docker_image = str(os.environ.get('DOCKER_GRADER_IMAGE'))
        self.log.debug('Image based on user role set to %s' % docker_image)
        return docker_image
