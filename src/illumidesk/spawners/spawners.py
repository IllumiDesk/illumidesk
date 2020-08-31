from dockerspawner import DockerSpawner

from typing import Dict

from illumidesk.authenticators.utils import user_is_an_instructor

from traitlets.traitlets import Bool


class IllumiDeskDockerSpawner(DockerSpawner):
    """Extends the DockerSpawner by defining the common behavior for our Spwaners that work
    with LTI versions 1.1 and 1.3
    """

    load_shared_folder_with_instructor = Bool(
        True,
        config=True,
        help="Mount the shared folder with Instructor role (Used with shared_folder_enabled env-var).",
    )

    def _volumes_to_binds(self, volumes: dict, binds: dict, mode: str = "rw") -> Dict[str, str]:
        """Binds volumes when spawning containers. This function overrides the DockerSpawner method to
        add determine shared directory permissions based on LTI role.

        Args:
            volumes: Volumes to mount.
            binds: Internal volumes to bind after the volumens are mounted.
            mode: Volume permissions. Defaults to "rw".

        Returns:
            Dict: returns collection that represents the volumes the container should mount (bind)
        """
        binds = super()._volumes_to_binds(volumes, binds, mode)
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
