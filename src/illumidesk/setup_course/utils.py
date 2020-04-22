import os
import sys
import logging
import docker
import subprocess
import time

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SetupUtils:
    """
    Utils class used to manage course setup configurations and updates.
    """

    def __init__(self):
        self.docker_client = docker.from_env()

    def restart_jupyterhub(self):
        """
        Restart jupyterhub using the docker client after updating configs.

        Raises:
          ContainerException if the container could not be restarted.
        """
        logger.debug('Received request to restart JupyterHub')
        jupyterhub_container_name = os.environ.get('JUPYTERHUB_SERVICE_NAME') or 'jupyterhub'
        illumidesk_dir = os.environ.get('ILLUMIDESK_DIR') or '/home/ubuntu/'

        containers = self.docker_client.containers.list(filters={'label': [f'com.docker.compose.service={jupyterhub_container_name}']})
        for container in containers:
            logger.debug('Found container %s, restarting ...' % container.id)
            try:
                # launch a new one to be attached in the proxy
                logger.info('Try to scale jupyterhub with docker-compose')
                subprocess.check_output(f'docker-compose --compatibility up -d --scale {jupyterhub_container_name}=2'.split(), cwd=f'{illumidesk_dir}')
                
                time.sleep(3)
                container.stop()
                # subprocess.check_output(f'docker-compose --compatibility up -d --scale {jupyterhub_container_name}=1'.split(), cwd=f'{illumidesk_dir}')
            except docker.errors.NotFound:
                logger.error('Jupyter container not found to restart it')
            except Exception as er:
                logger.error(f'Error trying to scale jupyterhub. {er}')
            break
