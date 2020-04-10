import sys
import logging
import docker

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
        jupyterhub_container_name = os.environ.get('JUPYTERHUB_SERVICE_NAME')
        containers = self.docker_client.containers.list(filters={'name': f'{jupyterhub_container_name}'})
        for container in containers:
            logger.debug('Found container %s, restarting ...' % jupyterhub_container_name)
            try:
                container.restart()
            except docker.errors.NotFound:
                logger.error('Grader container not found')
    