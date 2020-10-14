import os

from distutils.util import strtobool

from traitlets.config import Config


def test_jupyterhub_base_config(setup_jupyterhub_db, setup_jupyterhub_config_base):
    """
    Ensure all environment variables for the base config are set.
    """
    c = Config()
    c.JupyterHub.base_url = os.environ.get('JUPYTERHUB_BASE_URL')
    # JupyterHub postgres settings
    c.JupyterHub.db_url = 'postgresql://{user}:{password}@{host}:{port}/{db}'.format(
        user=os.environ.get('POSTGRES_JUPYTERHUB_USER'),
        password=os.environ.get('POSTGRES_JUPYTERHUB_PASSWORD'),
        host=os.environ.get('POSTGRES_JUPYTERHUB_HOST'),
        port=os.environ.get('POSTGRES_JUPYTERHUB_PORT'),
        db=os.environ.get('POSTGRES_JUPYTERHUB_DB'),
    )
    c.JupyterHub.shutdown_on_logout = bool(strtobool(os.environ.get('JUPYTERHUB_SHUTDOWN_ON_LOGOUT')))
    c.Authenticator.admin_users = {os.environ.get('JUPYTERHUB_ADMIN_USER')}
    c.Spawner.image = os.environ.get('DOCKER_END_USER_IMAGE')
    c.Spawner.cpu_limit = float(os.environ.get('SPAWNER_CPU_LIMIT'))
    c.Spawner.mem_limit = os.environ.get('SPAWNER_MEM_LIMIT')
    c.DockerSpawner.network_name = os.environ.get('DOCKER_NETWORK_NAME')
    docker_spawn_command = os.environ.get('DOCKER_SPAWN_CMD')
    exchange_dir = os.environ.get('EXCHANGE_DIR')
    notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR')

    assert c.Authenticator.admin_users == {'admin0'}

    assert c.DockerSpawner.network_name == 'test-network'

    assert c.JupyterHub.db_url == 'postgresql://foobar:abc123@jupyterhub-db:5432/jupyterhub'
    assert c.JupyterHub.shutdown_on_logout == True  # noqa: E712

    assert c.Spawner.cpu_limit == 0.5
    assert c.Spawner.mem_limit == '2G'

    assert docker_spawn_command == 'single_user_test.sh'
    assert exchange_dir == '/path/to/exchange'
    assert notebook_dir == '/home/saturn'
