from dockerspawner import DockerSpawner

from illumidesk.authenticators.utils import user_is_an_instructor

from illumidesk.spawners.hooks import custom_auth_state_hook
from illumidesk.spawners.hooks import custom_pre_spawn_hook

from traitlets.traitlets import Bool


class IllumiDeskBaseDockerSpawner(DockerSpawner):
    """Extends the DockerSpawner by defining the common behavior for our Spwaners that work
    with LTI versions 1.1 and 1.3
    """

    load_shared_folder_with_instructor = Bool(
        True,
        config=True,
        help="Mount the shared folder with Instructor role (Used with shared_folder_enabled env-var).",
    )

    def _volumes_to_bind(self, volumes: dict, binds: dict, mode: str = "rw"):
        """Binds volumes when spawning containers.

        Args:
            volumes ([type]): [description]
            binds ([type]): [description]
            mode (str, optional): [description]. Defaults to "rw".

        Returns:
            [type]: [description]
        """
        binds = self._volumes_to_bind(volumes, binds, mode)
        if self.load_shared_folder_with_instructor is False and user_is_an_instructor(self.environment['USER_ROLE']):
            self.log.debug(f'binds loaded from volumes setting: {binds}')
            shared_vol_key = ''
            for k, v in binds.items():
                if '/shared' in v['bind']:
                    shared_vol_key = k
                    break
            if shared_vol_key:
                self.log.debug('Removing shared folder for instructor')
                del binds[shared_vol_key]
                self.log.debug(f'binds without the shared folder: {binds}')
        return binds

    def auth_state_hook(self, spawner: DockerSpawner, auth_state: dict) -> None:
        """[summary]

        Args:
            spawner (DockerSpawner): [description]
            auth_state (dict): [description]
        """
        # call our custom hook from here without issue related with 'invalid arguments number given'
        custom_auth_state_hook(spawner, auth_state)

    def pre_spawn_hook(self, spawner) -> None:
        """[summary]

        Args:
            spawner ([type]): [description]
        """
        custom_pre_spawn_hook(spawner)

    def start(self) -> None:
        """[summary]

        Returns:
            [type]: [description]
        """
        self.image = self._get_image_name()
        self.log.debug('Starting with image: %s' % self.image)
        return super().start()
