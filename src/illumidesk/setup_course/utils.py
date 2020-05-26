import os
import logging
import subprocess
import sys
import time

import docker
from docker.errors import NotFound


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SetupUtils:
    """
    Utils class used to manage course setup configurations and updates.
    """

    def __init__(self):
        self.docker_client = docker.from_env()
        self.jupyterhub_container_name = os.environ.get('JUPYTERHUB_SERVICE_NAME') or 'jupyterhub'
        self.illumidesk_dir = os.environ.get('ILLUMIDESK_DIR')
        if not self.illumidesk_dir:
            raise EnvironmentError('Missing or null ILLUMIDESK_DIR env var value.')

    def restart_jupyterhub(self) -> None:
        """
        Initiates a jupyterhubb rolling update. In order to load changes in configuration file,
        the jupyterhub container is replaced with new one, then the older is stopped.
        Traefik can redirect the traffic to new one service few seconds later.
        """
        logger.debug('Received request to restart JupyterHub')
        containers = self.docker_client.containers.list(
            filters={'label': [f'com.docker.compose.service={self.jupyterhub_container_name}']}
        )
        for container in containers:
            logger.debug(f'Found a jupyterhub container (running): {container.id}')
            try:
                # launch a new one to be attached in the proxy
                logger.info('Trying to scale jupyterhub with docker-compose')
                subprocess.check_output(
                    f'docker-compose --compatibility up -d --scale {self.jupyterhub_container_name}=2'.split(),
                    cwd=f'{self.illumidesk_dir}',
                )
                time.sleep(3)
                logger.debug(f'The container: {container.id} is stopping...')
                container.stop()
                time.sleep(1)
            except NotFound:
                logger.error('Jupyterhub container not found, unable to proceed with rolling update.')
            except Exception as er:
                logger.error(f'Error trying to scale jupyterhub: {er}')
            break
        self.docker_client.containers.prune(
            filters={'label': [f'com.docker.compose.service={self.jupyterhub_container_name}']}
        )
        logger.debug(f'Pruning unused jupyterhub containers {self.jupyterhub_container_name}')
