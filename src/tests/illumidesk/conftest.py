import pytest
import uuid

from Crypto.PublicKey import RSA

from docker.errors import NotFound

from unittest.mock import Mock
from unittest.mock import MagicMock


@pytest.fixture(scope="function")
def jupyterhub_api_environ(monkeypatch):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('JUPYTERHUB_API_TOKEN', str(uuid.uuid4()))
    monkeypatch.setenv('JUPYTERHUB_API_URL', 'localhost/hub/api')


@pytest.fixture(scope="function")
def lti_config_environ(monkeypatch, pem_file):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('LTI13_PRIVATE_KEY', pem_file)


@pytest.fixture(scope="function")
def mock_docker_client_cotainers_not_found():
    """
    Creates a DockerClient mock object
    """
    docker_client = Mock(spec='docker.DockerClient')

    def _container_not_exists(name):
        raise NotFound(f'container: {name} not exists')

    docker_client.containers = MagicMock()
    docker_client.containers.get.side_effect = lambda name: _container_not_exists(name)


@pytest.fixture
def pem_file(tmp_path):
    key = RSA.generate(2048)
    key_path = f'{tmp_path}/private.key'
    with open(key_path, 'wb') as content_file:
        content_file.write(key.exportKey('PEM'))
    return key_path


@pytest.fixture(scope="function")
def setup_course_environ(monkeypatch, tmp_path, jupyterhub_api_environ):
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
