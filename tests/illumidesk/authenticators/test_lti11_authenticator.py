import pytest
import json

from tornado.web import RequestHandler
from tornado.httputil import HTTPServerRequest

from typing import Dict

from unittest.mock import Mock
from unittest.mock import MagicMock
from unittest.mock import patch

from illumidesk.authenticators.validator import LTI11LaunchValidator
from illumidesk.authenticators.authenticator import LTI11Authenticator

from illumidesk.authenticators.utils import LTIUtils


def mock_lti11_instructor_args(lms_vendor: str) -> Dict[str, str]:
    args = {
        'oauth_consumer_key': ['my_consumer_key'.encode()],
        'oauth_signature_method': ['HMAC-SHA1'.encode()],
        'oauth_timestamp': ['1585947271'.encode()],
        'oauth_nonce': ['01fy8HKIASKuD9gK9vWUcBj9fql1nOCWfOLPzeylsmg'.encode()],
        'oauth_version': ['1.0'.encode()],
        'context_id': ['888efe72d4bbbdf90619353bb8ab5965ccbe9b3f'.encode()],
        'context_label': ['intro101'.encode()],
        'context_title': ['intro101'.encode()],
        'ext_roles': ['urn:lti:instrole:ims/lis/Learner'.encode()],
        'launch_presentation_document_target': ['iframe'.encode()],
        'launch_presentation_height': ['1000'.encode()],
        'launch_presentation_locale': ['en'.encode()],
        'launch_presentation_return_url': [
            'https: //illumidesk.instructure.com/courses/161/external_content/success/external_tool_redirect'.encode()
        ],
        'launch_presentation_width': ['1000'.encode()],
        'lis_person_contact_email_primary': ['foo@example.com'.encode()],
        'lis_person_name_family': ['Bar'.encode()],
        'lis_person_name_full': ['Foo Bar'.encode()],
        'lis_person_name_given': ['Foo'.encode()],
        'lti_message_type': ['basic-lti-launch-request'.encode()],
        'lti_version': ['LTI-1p0'.encode()],
        'oauth_callback': ['about:blank'.encode()],
        'resource_link_id': ['888efe72d4bbbdf90619353bb8ab5965ccbe9b3f'.encode()],
        'resource_link_title': ['IllumiDesk'.encode()],
        'roles': ['Instructor'.encode()],
        'tool_consumer_info_product_family_code': [lms_vendor.encode()],
        'tool_consumer_info_version': ['cloud'.encode()],
        'tool_consumer_instance_contact_email': ['notifications@mylms.com'.encode()],
        'tool_consumer_instance_guid': [
            'srnuz6h1U8kOMmETzoqZTJiPWzbPXIYkAUnnAJ4u:test-lms'.encode()
        ],
        'tool_consumer_instance_name': ['myorg'.encode()],
        'user_id': ['185d6c59731a553009ca9b59ca3a885100000'.encode()],
        'user_image': ['https://lms.example.com/avatar-50.png'.encode()],
        'oauth_signature': ['abc123'.encode()],
    }
    return args


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_canvas_fields(lti11_authenticator):
    '''
    Do we get a valid username when sending an argument with the custom canvas id?
    '''
    with patch.object(
        LTI11LaunchValidator, 'validate_launch_request', return_value=True
    ):
        authenticator = LTI11Authenticator()
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(arguments=mock_lti11_instructor_args('canvas'), headers={}, items=[],),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_other_lms_vendor(
    lti11_authenticator,
):
    '''
    Do we get a valid username with lms vendors other than canvas?
    '''
    utils = LTIUtils()
    utils.convert_request_to_dict = MagicMock(name='convert_request_to_dict')
    utils.convert_request_to_dict(3, 4, 5, key='value')
    with patch.object(
        LTI11LaunchValidator, 'validate_launch_request', return_value=True
    ):
        authenticator = LTI11Authenticator()
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(arguments=mock_lti11_instructor_args('moodle'), headers={}, items=[],),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
async def test_authenticator_uses_ltivalidator():
    with patch.object(
        LTI11LaunchValidator, 'validate_launch_request', return_value=True
    ) as mock_validator:

        authenticator = LTI11Authenticator()
        handler = Mock(spec=RequestHandler)
        request = HTTPServerRequest(method='POST', connection=Mock(),)
        handler.request = request

        handler.request.arguments = mock_lti11_instructor_args('lmsvendor')
        handler.request.get_argument = lambda x, strip=True: mock_lti11_instructor_args(
            'lmsvendor'
        )[x][0].decode()

        _ = await authenticator.authenticate(handler, None)
        assert mock_validator.called


@pytest.mark.asyncio
async def test_authenticator_invokes_validator_with_decoded_dict():
    with patch.object(
        LTI11LaunchValidator, 'validate_launch_request', return_value=True
    ) as mock_validator:

        authenticator = LTI11Authenticator()
        handler = Mock(spec=RequestHandler)
        request = HTTPServerRequest(method='POST', uri='/hub', host='example.com')
        handler.request = request
        handler.request.protocol = 'https'
        handler.request.arguments = mock_lti11_instructor_args('canvas')
        handler.request.get_argument = lambda x, strip=True: mock_lti11_instructor_args('canvas')[
            x
        ][0].decode()

        _ = await authenticator.authenticate(handler, None)
        # check our validator was called
        assert mock_validator.called
        decoded_args = {
            k: handler.request.get_argument(k, strip=False)
            for k, v in mock_lti11_instructor_args('canvas').items()
        }
        # check validator was called with correct dict params (decoded)
        mock_validator.assert_called_with('https://example.com/hub', {}, decoded_args)
