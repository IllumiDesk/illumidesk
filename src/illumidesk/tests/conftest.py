import pytest

from docker.errors import NotFound

from unittest.mock import Mock
from unittest.mock import MagicMock


@pytest.fixture(scope="function")
def setup_course_environ(monkeypatch, tmp_path):
    """
    Set the environment variables used in Course class
    """
    monkeypatch.setenv('MNT_ROOT', str(tmp_path))
    monkeypatch.setenv('NB_UID', '10001')
    monkeypatch.setenv('NB_GID', '100')


@pytest.fixture(scope="function")
def setup_utils_environ(monkeypatch, tmp_path):
    """
    Set the enviroment variables used in SetupUtils class
    """
    monkeypatch.setenv('JUPYTERHUB_SERVICE_NAME', 'jupyterhub')
    monkeypatch.setenv('ILLUMIDESK_DIR', '/home/foo/illumidesk_deployment')


@pytest.fixture(scope="function")
def setup_utils_environ_empty_illumidesk_dir(monkeypatch, tmp_path):
    """
    Set the enviroment variables used in SetupUtils class
    """
    monkeypatch.setenv('JUPYTERHUB_SERVICE_NAME', 'jupyterhub')
    monkeypatch.setenv('ILLUMIDESK_DIR', '')


@pytest.fixture(scope="function")
def docker_containers():
    """
    Creates a DockerClient mock object
    """
    docker_client = Mock(spec='docker.DockerClient')

    def _container_not_exists(name):
        raise NotFound(f'container: {name} not exists')

    docker_client.containers = MagicMock()
    docker_client.containers.get.side_effect = lambda name: _container_not_exists(name)


@pytest.fixture(scope="function")
def setup_course_environ(monkeypatch, tmp_path):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('MNT_ROOT', str(tmp_path))
    monkeypatch.setenv('NB_UID', '10001')
    monkeypatch.setenv('NB_GID', '100')


@pytest.fixture(scope='function')
def test_client(monkeypatch, tmp_path):
    """
    Before to import the quart-app we define the env-vars required
    """
    monkeypatch.setenv('JUPYTERHUB_CONFIG_PATH', str(tmp_path))
    # important than environ reads JUPYTERHUB_CONFIG_PATH variable before
    # app initialization
    from illumidesk.setup_course.app import app

    return app.test_client()
