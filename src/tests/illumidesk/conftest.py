import pytest
import uuid

from Crypto.PublicKey import RSA

from docker.errors import NotFound

from tornado.web import Application
from tornado.web import RequestHandler

from typing import Any
from typing import Dict

from unittest.mock import Mock
from unittest.mock import MagicMock

from illumidesk.handlers.lms_grades import LTIGradesSenderControlFile
from illumidesk.authenticators.utils import LTIUtils


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
def jupyterhub_api_environ(monkeypatch):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('JUPYTERHUB_API_TOKEN', str(uuid.uuid4()))
    monkeypatch.setenv('JUPYTERHUB_API_URL', 'https://localhost/hub/api')


@pytest.fixture(scope='function')
def lti_config_environ(monkeypatch, pem_file):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('LTI13_PRIVATE_KEY', pem_file)


@pytest.fixture(scope='function')
def lti13_login_params(
    client_id: str = '125900000000000085',
    iss: str = 'https://platform.vendor.com',
    login_hint: str = '185d6c59731a553009ca9b59ca3a885104ecb4ad',
    target_link_uri: str = 'https://edu.example.com/hub',
    lti_message_hint: str = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2ZXJpZmllciI6IjFlMjk2NjEyYjZmMjdjYmJkZTg5YmZjNGQ1ZmQ5ZDBhMzhkOTcwYzlhYzc0NDgwYzdlNTVkYzk3MTQyMzgwYjQxNGNiZjMwYzM5Nzk1Y2FmYTliOWYyYTgzNzJjNzg3MzAzNzAxZDgxMzQzZmRmMmIwZDk5ZTc3MWY5Y2JlYWM5IiwiY2FudmFzX2RvbWFpbiI6ImlsbHVtaWRlc2suaW5zdHJ1Y3R1cmUuY29tIiwiY29udGV4dF90eXBlIjoiQ291cnNlIiwiY29udGV4dF9pZCI6MTI1OTAwMDAwMDAwMDAwMTM2LCJleHAiOjE1OTE4MzMyNTh9.uYHinkiAT5H6EkZW9D7HJ1efoCmRpy3Id-gojZHlUaA',
) -> Dict[str, Any]:
    """
    Creates a dictionary with k/v's that emulates an initial login request.
    """
    params = {
        'client_id': [client_id.encode()],
        'iss': [iss.encode()],
        'login_hint': [login_hint.encode()],
        'target_link_uri': [target_link_uri.encode()],
        'lti_message_hint': [lti_message_hint.encode()],
    }
    return params


@pytest.fixture(scope='function')
def lti13_auth_params(
    client_id: str = '125900000000000081',
    redirect_uri: str = 'https://acme.illumidesk.com/hub/oauth_callback',
    lti_message_hint: str = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2ZXJpZmllciI6IjFlMjk2NjEyYjZmMjdjYmJkZTg5YmZjNGQ1ZmQ5ZDBhMzhkOTcwYzlhYzc0NDgwYzdlNTVkYzk3MTQyMzgwYjQxNGNiZjMwYzM5Nzk1Y2FmYTliOWYyYTgzNzJjNzg3MzAzNzAxZDgxMzQzZmRmMmIwZDk5ZTc3MWY5Y2JlYWM5IiwiY2FudmFzX2RvbWFpbiI6ImlsbHVtaWRlc2suaW5zdHJ1Y3R1cmUuY29tIiwiY29udGV4dF90eXBlIjoiQ291cnNlIiwiY29udGV4dF9pZCI6MTI1OTAwMDAwMDAwMDAwMTM2LCJleHAiOjE1OTE4MzMyNTh9.uYHinkiAT5H6EkZW9D7HJ1efoCmRpy3Id-gojZHlUaA',
    login_hint: str = '185d6c59731a553009ca9b59ca3a885104ecb4ad',
    state: str = 'eyJzdGF0ZV9pZCI6ICI2ZjBlYzE1NjlhM2E0MDJkYWM2MTYyNjM2MWQwYzEyNSIsICJuZXh0X3VybCI6ICIvIn0=',
    nonce: str = '38048502278109788461591832959',
) -> Dict[str, Any]:
    """
    Creates a dictionary with k/v's that emulates a login request.
    """
    params = {
        'response_type': ['id_token'.encode()],
        'scope': ['openid'.encode()],
        'client_id': [client_id.encode()],
        'redirect_uri': [redirect_uri.encode()],
        'response_mode': ['form_post'.encode()],
        'lti_message_hint': [lti_message_hint.encode()],
        'prompt': ['none'.encode()],
        'login_hint': [login_hint.encode()],
        'state': [state.encode()],
        'nonce': [nonce.encode()],
    }
    return params


@pytest.fixture(scope='function')
def lti13_auth_params_dict(lti13_auth_params) -> Dict[str, Any]:
    """
    Return the initial LTI 1.3 authorization request as a dict
    """
    utils = LTIUtils()
    args = utils.convert_request_to_dict(lti13_auth_params)
    return args


@pytest.fixture(scope='function')
def lti13_login_params_dict(lti13_login_params) -> Dict[str, Any]:
    """
    Return the initial LTI 1.3 authorization request as a dict
    """
    utils = LTIUtils()
    args = utils.convert_request_to_dict(lti13_login_params)
    return args


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
def test_quart_client(monkeypatch, tmp_path):
    """
    Set the env-vars required by quart-based application
    """
    monkeypatch.setenv('JUPYTERHUB_CONFIG_PATH', str(tmp_path))
    # important than environ reads JUPYTERHUB_CONFIG_PATH variable before
    # app initialization
    from illumidesk.setup_course.app import app

    return app.test_client()
