import pytest
import uuid

from Crypto.PublicKey import RSA

from docker.errors import NotFound

from tornado.web import Application
from tornado.web import RequestHandler

from unittest.mock import Mock
from unittest.mock import MagicMock

from illumidesk.handlers.lms_grades import LTIGradesSenderControlFile


@pytest.fixture(scope='module')
def app():
    class TestHandler(RequestHandler):
        def get(self):
            self.write("test")

        def post(self):
            self.write("test")

    application = Application([(r'/', TestHandler),])  # noqa: E231
    return application


@pytest.fixture(scope='function')
def jupyterhub_api_environ(monkeypatch):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('JUPYTERHUB_API_TOKEN', str(uuid.uuid4()))
    monkeypatch.setenv('JUPYTERHUB_API_URL', 'https://localhost/hub/api')


@pytest.fixture(scope="function")
def lti_config_environ(monkeypatch, pem_file):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('LTI13_PRIVATE_KEY', pem_file)


@pytest.fixture
def pem_file(tmp_path):
    """
    Create a test private key file used with LTI 1.3 request/reponse flows
    """
    key = RSA.generate(2048)
    key_path = f'{tmp_path}/private.key'
    with open(key_path, 'wb') as content_file:
        content_file.write(key.exportKey('PEM'))
    return key_path


@pytest.fixture
def reset_file_loaded():
    """
    Set flag to false to reload control file used in LTIGradesSenterControlFile class
    """
    LTIGradesSenderControlFile.FILE_LOADED = False


@pytest.fixture(scope='function')
def setup_course_environ(monkeypatch, tmp_path, jupyterhub_api_environ):
    """
    Set the environment variables used in Course class`
    """
    monkeypatch.setenv('MNT_ROOT', str(tmp_path))
    monkeypatch.setenv('NB_UID', '10001')
    monkeypatch.setenv('NB_GID', '100')


@pytest.fixture(scope='function')
def setup_course_hook_environ(monkeypatch, jupyterhub_api_environ):
    """
    Set the environment variables used in the setup_course_hook function
    """
    monkeypatch.setenv('ANNOUNCEMENT_SERVICE_PORT', '8889')
    monkeypatch.setenv('DOCKER_SETUP_COURSE_SERVICE_NAME', 'setup-course')
    monkeypatch.setenv('DOCKER_SETUP_COURSE_PORT', '8000')
    monkeypatch.setenv('ORGANIZATION_NAME', 'test-org')


@pytest.fixture(scope='function')
def setup_utils_environ(monkeypatch, tmp_path):
    """
    Set the enviroment variables used in SetupUtils class
    """
    monkeypatch.setenv('JUPYTERHUB_SERVICE_NAME', 'jupyterhub')
    monkeypatch.setenv('ILLUMIDESK_DIR', '/home/foo/illumidesk_deployment')


@pytest.fixture(scope='function')
def docker_client_cotainers_not_found():
    """
    Creates a DockerClient mock object where the container name does not exist
    """
    docker_client = Mock(spec='docker.DockerClient')

    def _container_not_exists(name):
        raise NotFound(f'container: {name} not exists')

    docker_client.containers = MagicMock()
    docker_client.containers.get.side_effect = lambda name: _container_not_exists(name)


@pytest.fixture(scope='function')
def test_quart_client(monkeypatch, tmp_path):
    """
    Set the env-vars required by quart-based application
    """
    monkeypatch.setenv('JUPYTERHUB_CONFIG_PATH', str(tmp_path))
    # important than environ reads JUPYTERHUB_CONFIG_PATH variable before
    # app initialization
    from illumidesk.setup_course.app import app

    return app.test_client()
