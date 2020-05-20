import pytest

from tornado.web import HTTPError

from typing import Dict

from illumidesk.authenticators.validator import LTI13LaunchValidator


def mock_lti13_claims(lms_vendor: str = 'canvas') -> Dict[str, str]:
    jws = {
        'https://purl.imsglobal.org/spec/lti/claim/message_type': 'LtiResourceLinkRequest',
        'https://purl.imsglobal.org/spec/lti/claim/version': '1.3.0',
        'https://purl.imsglobal.org/spec/lti/claim/resource_link': {
            'id': 'b81accac78543cb7cd239f3792bcfdc7c6efeadb',
            'description': 'Assignment to introduct who we are',
            'title': 'Introduction Assignment',
            'validation_context': None,
            'errors': {'errors': {}},
        },
        'aud': '125900000000000071',
        'azp': '125900000000000071',
        'https://purl.imsglobal.org/spec/lti/claim/deployment_id': '847:b81accac78543cb7cd239f3792bcfdc7c6efeadb',
        'exp': 1589843421,
        'iat': 1589839821,
        'iss': 'https://canvas.instructure.com',
        'nonce': '125687018437687229621589839822',
        'sub': '8171934b-f5e2-4f4e-bdbd-6d798615b93e',
        'https://purl.imsglobal.org/spec/lti/claim/target_link_uri': 'https://myedu.illumidesk.com/hub',
        'https://purl.imsglobal.org/spec/lti/claim/context': {
            'id': 'b81accac78543cb7cd239f3792bcfdc7c6efeadb',
            'label': 'intro101',
            'title': 'intro101',
            'type': ['http://purl.imsglobal.org/vocab/lis/v2/course#CourseOffering'],
            'validation_context': None,
            'errors': {'errors': {}},
        },
        'https://purl.imsglobal.org/spec/lti/claim/tool_platform': {
            'guid': 'srnuz6h1U8kOMmETzoqZTJiPWzbPXIYkAUnnAJ4u:canvas-lms',
            'name': 'Illumidesk',
            'version': 'cloud',
            'product_family_code': lms_vendor,
            'validation_context': None,
            'errors': {'errors': {}},
        },
        'https://purl.imsglobal.org/spec/lti/claim/launch_presentation': {
            'document_target': 'iframe',
            'height': 400,
            'width': 800,
            'return_url': 'https://illumidesk.instructure.com/courses/147/external_content/success/external_tool_redirect',
            'locale': 'en',
            'validation_context': None,
            'errors': {'errors': {}},
        },
        'locale': 'en',
        'https://purl.imsglobal.org/spec/lti/claim/roles': [
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner',
            'http://purl.imsglobal.org/vocab/lis/v2/system/person#User',
        ],
        'https://purl.imsglobal.org/spec/lti/claim/custom': {'email': 'student1@example.com'},
        'errors': {'errors': {}},
        'https://purl.imsglobal.org/spec/lti-ags/claim/endpoint': {
            'scope': [
                'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem',
                'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly',
                'https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly',
                'https://purl.imsglobal.org/spec/lti-ags/scope/score',
            ],
            'lineitems': 'https://illumidesk.instructure.com/api/lti/courses/147/line_items',
            'validation_context': None,
            'errors': {'errors': {}},
        },
        'picture': 'https://canvas.instructure.com/images/messages/avatar-50.png',
        'email': 'student1@example.com',
        'name': 'Student1 Bar',
        'given_name': 'Student1',
        'family_name': 'Bar',
        'https://purl.imsglobal.org/spec/lti/claim/lis': {
            'person_sourcedid': None,
            'course_offering_sourcedid': None,
            'validation_context': None,
            'errors': {'errors': {}},
        },
        'https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice': {
            'context_memberships_url': 'https://illumidesk.instructure.com/api/lti/courses/147/names_and_roles',
            'service_versions': ['2.0'],
            'validation_context': None,
            'errors': {'errors': {}},
        },
    }
    required_claims = {
        'https://purl.imsglobal.org/spec/lti/claim/message_type': 'LtiResourceLinkRequest',
        'https://purl.imsglobal.org/spec/lti/claim/version': '1.3.0',
        'https://purl.imsglobal.org/spec/lti/claim/deployment_id': '847:b81accac78543cb7cd239f3792bcfdc7c6efeadb',
        'https://purl.imsglobal.org/spec/lti/claim/target_link_uri': 'https://edu.example.com/hub',
        'https://purl.imsglobal.org/spec/lti/claim/resource_link': {
            'id': 'b81accac78543cb7cd239f3792bcfdc7c6efeadb',
        },  # noqa: E231
        'https://purl.imsglobal.org/spec/lti/claim/roles': [
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor",
        ],
    }
    return required_claims


def test_validate_missing_required_claims_in_resource_link_request():
    """
    Is the JWT valid with an incorrect message type claim?
    """
    validator = LTI13LaunchValidator()
    fake_jws = {
        'key1': 'value1',
    }

    with pytest.raises(HTTPError):
        validator.validate_launch_request(fake_jws)


def test_validate_invalid_resource_link_request_message_type_claim_value():
    """
    Is the JWT valid with an incorrect message type claim?
    """
    validator = LTI13LaunchValidator()
    jws = mock_lti13_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/message_type'] = 'FakeLinkRequest'

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_invalid_version_request_claim_value():
    """
    Is the JWT valid with an incorrect version claim?
    """
    validator = LTI13LaunchValidator()
    jws = mock_lti13_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/version'] = '1.0.0'

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_empty_deployment_id_request_claim_value():
    """
    Is the JWT valid with an empty deployment_id claim?
    """
    validator = LTI13LaunchValidator()
    jws = mock_lti13_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/deployment_id'] = ''

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_empty_target_link_uri_request_claim_value():
    """
    Is the JWT valid with an empty target link uri claim?
    """
    validator = LTI13LaunchValidator()
    jws = mock_lti13_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/target_link_uri'] = ''

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_empty_resource_link_id_request_claim_value():
    """
    Is the JWT valid with an empty resource request id uri claim?
    """
    validator = LTI13LaunchValidator()
    jws = mock_lti13_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/resource_link']['id'] = ''

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_empty_roles_claim_value():
    """
    Is the JWT valid with an empty roles claim value?
    """
    validator = LTI13LaunchValidator()
    jws = mock_lti13_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/roles'] = ''

    assert validator.validate_launch_request(jws)
