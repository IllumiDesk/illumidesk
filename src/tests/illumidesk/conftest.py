import pytest
import uuid

from Crypto.PublicKey import RSA

from tornado.web import Application
from tornado.web import RequestHandler

from unittest.mock import patch

from illumidesk.grades.sender_controlfile import LTIGradesSenderControlFile
from illumidesk.authenticators.utils import LTIUtils

from tornado.httpclient import AsyncHTTPClient

from tests.illumidesk.factory import factory_http_response
from tests.illumidesk.mocks import mock_handler


@pytest.fixture(scope='module')
def auth_state_dict():
    authenticator_auth_state = {
        'name': 'student1',
        'auth_state': {
            'course_id': 'intro101',
            'course_lineitems': 'my.platform.com/api/lti/courses/1/line_items',
            'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
            'user_role': 'Learner',
            'workspace_type': 'notebook',
        },
    }
    return authenticator_auth_state


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


@pytest.fixture(scope='function')
def lti_config_environ(monkeypatch, pem_file):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('LTI13_PRIVATE_KEY', pem_file)
    monkeypatch.setenv('LTI13_TOKEN_URL', 'https://my.platform.domain/login/oauth2/token')
    monkeypatch.setenv('LTI13_CLIENT_ID', '000000000000001')


@pytest.fixture(scope='function')
def lti11_complete_launch_args():
    """
    Valid response when retrieving jwks from the platform.
    """
    args = {
        'oauth_callback': ['about:blank'.encode()],
        'oauth_consumer_key': ['my_consumer_key'.encode()],
        'oauth_signature_method': ['HMAC-SHA1'.encode()],
        'oauth_timestamp': ['1585947271'.encode()],
        'oauth_nonce': ['01fy8HKIASKuD9gK9vWUcBj9fql1nOCWfOLPzeylsmg'.encode()],
        'oauth_signature': ['abc123'.encode()],
        'oauth_version': ['1.0'.encode()],
        'context_id': ['888efe72d4bbbdf90619353bb8ab5965ccbe9b3f'.encode()],
        'context_label': ['intro101'.encode()],
        'context_title': ['intro101'.encode()],
        'custom_canvas_assignment_title': ['test-assignment'.encode()],
        'custom_canvas_user_login_id': ['student1'.encode()],
        'custom_worskpace_type': ['foo'.encode()],
        'ext_roles': ['urn:lti:instrole:ims/lis/Learner'.encode()],
        'launch_presentation_document_target': ['iframe'.encode()],
        'launch_presentation_height': ['1000'.encode()],
        'launch_presentation_locale': ['en'.encode()],
        'launch_presentation_return_url': [
            'https: //illumidesk.instructure.com/courses/161/external_content/success/external_tool_redirect'.encode()
        ],
        'launch_presentation_width': ['1000'.encode()],
        'lis_outcome_service_url': [
            'http://www.imsglobal.org/developers/LTI/test/v1p1/common/tool_consumer_outcome.php?b64=MTIzNDU6OjpzZWNyZXQ='.encode()
        ],
        'lis_person_contact_email_primary': ['student1@example.com'.encode()],
        'lis_person_name_family': ['Bar'.encode()],
        'lis_person_name_full': ['Foo Bar'.encode()],
        'lis_person_name_given': ['Foo'.encode()],
        'lti_message_type': ['basic-lti-launch-request'.encode()],
        'lis_result_sourcedid': ['feb-123-456-2929::28883'.encode()],
        'lti_version': ['LTI-1p0'.encode()],
        'resource_link_id': ['888efe72d4bbbdf90619353bb8ab5965ccbe9b3f'.encode()],
        'resource_link_title': ['IllumiDesk'.encode()],
        'roles': ['Learner'.encode()],
        'tool_consumer_info_product_family_code': ['canvas'.encode()],
        'tool_consumer_info_version': ['cloud'.encode()],
        'tool_consumer_instance_contact_email': ['notifications@mylms.com'.encode()],
        'tool_consumer_instance_guid': ['srnuz6h1U8kOMmETzoqZTJiPWzbPXIYkAUnnAJ4u:test-lms'.encode()],
        'tool_consumer_instance_name': ['myorg'.encode()],
        'user_id': ['185d6c59731a553009ca9b59ca3a885100000'.encode()],
        'user_image': ['https://lms.example.com/avatar-50.png'.encode()],
    }
    return args


@pytest.fixture(scope='function')
def lti13_login_params():
    """
    Creates a dictionary with k/v's that emulates an initial login request.
    """
    client_id = '125900000000000085'
    iss = 'https://platform.vendor.com'
    login_hint = '185d6c59731a553009ca9b59ca3a885104ecb4ad'
    target_link_uri = 'https://edu.example.com/hub'
    lti_message_hint = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2ZXJpZmllciI6IjFlMjk2NjEyYjZmMjdjYmJkZTg5YmZjNGQ1ZmQ5ZDBhMzhkOTcwYzlhYzc0NDgwYzdlNTVkYzk3MTQyMzgwYjQxNGNiZjMwYzM5Nzk1Y2FmYTliOWYyYTgzNzJjNzg3MzAzNzAxZDgxMzQzZmRmMmIwZDk5ZTc3MWY5Y2JlYWM5IiwiY2FudmFzX2RvbWFpbiI6ImlsbHVtaWRlc2suaW5zdHJ1Y3R1cmUuY29tIiwiY29udGV4dF90eXBlIjoiQ291cnNlIiwiY29udGV4dF9pZCI6MTI1OTAwMDAwMDAwMDAwMTM2LCJleHAiOjE1OTE4MzMyNTh9.uYHinkiAT5H6EkZW9D7HJ1efoCmRpy3Id-gojZHlUaA'

    params = {
        'client_id': [client_id.encode()],
        'iss': [iss.encode()],
        'login_hint': [login_hint.encode()],
        'target_link_uri': [target_link_uri.encode()],
        'lti_message_hint': [lti_message_hint.encode()],
    }
    return params


@pytest.fixture(scope='function')
def lti13_auth_params():
    """
    Creates a dictionary with k/v's that emulates a login request.
    """
    client_id = '125900000000000081'
    redirect_uri = 'https://acme.illumidesk.com/hub/oauth_callback'
    lti_message_hint = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2ZXJpZmllciI6IjFlMjk2NjEyYjZmMjdjYmJkZTg5YmZjNGQ1ZmQ5ZDBhMzhkOTcwYzlhYzc0NDgwYzdlNTVkYzk3MTQyMzgwYjQxNGNiZjMwYzM5Nzk1Y2FmYTliOWYyYTgzNzJjNzg3MzAzNzAxZDgxMzQzZmRmMmIwZDk5ZTc3MWY5Y2JlYWM5IiwiY2FudmFzX2RvbWFpbiI6ImlsbHVtaWRlc2suaW5zdHJ1Y3R1cmUuY29tIiwiY29udGV4dF90eXBlIjoiQ291cnNlIiwiY29udGV4dF9pZCI6MTI1OTAwMDAwMDAwMDAwMTM2LCJleHAiOjE1OTE4MzMyNTh9.uYHinkiAT5H6EkZW9D7HJ1efoCmRpy3Id-gojZHlUaA'
    login_hint = '185d6c59731a553009ca9b59ca3a885104ecb4ad'
    state = 'eyJzdGF0ZV9pZCI6ICI2ZjBlYzE1NjlhM2E0MDJkYWM2MTYyNjM2MWQwYzEyNSIsICJuZXh0X3VybCI6ICIvIn0='
    nonce = '38048502278109788461591832959'

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
def lti13_auth_params_dict(lti13_auth_params):
    """
    Return the initial LTI 1.3 authorization request as a dict
    """
    utils = LTIUtils()
    args = utils.convert_request_to_dict(lti13_auth_params)
    return args


@pytest.fixture(scope='function')
def lti13_login_params_dict(lti13_login_params):
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
def grades_controlfile_reset_file_loaded():
    """
    Set flag to false to reload control file used in LTIGradesSenterControlFile class
    """
    LTIGradesSenderControlFile.FILE_LOADED = False


@pytest.fixture(scope='function')
def setup_image_environ(monkeypatch):
    """
    Set the enviroment variables used to identify images assigned by
    role and/or workspace type.
    """
    monkeypatch.setenv('DOCKER_STANDARD_IMAGE', 'standard_image')
    monkeypatch.setenv('DOCKER_LEARNER_IMAGE', 'learner_image')
    monkeypatch.setenv('DOCKER_INSTRUCTOR_IMAGE', 'instructor_i/mage')
    monkeypatch.setenv('DOCKER_GRADER_IMAGE', 'grader_image')
    monkeypatch.setenv('DOCKER_THEIA_IMAGE', 'theia_image')
    monkeypatch.setenv('DOCKER_RSTUDIO_IMAGE', 'rstudio_image')
    monkeypatch.setenv('DOCKER_VSCODE_IMAGE', 'vscode_image')


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


@pytest.fixture
def http_async_httpclient_with_simple_response(request):
    """
    Creates a patch of AsyncHttpClient.fetch method, useful when other tests are making http request
    """
    local_handler = mock_handler(RequestHandler)
    test_request_body_param = request.param if hasattr(request, 'param') else {'message': 'ok'}
    with patch.object(
        AsyncHTTPClient,
        'fetch',
        return_value=factory_http_response(handler=local_handler.request, body=test_request_body_param),
    ):
        yield AsyncHTTPClient()
