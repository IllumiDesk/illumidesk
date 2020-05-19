import pytest

from tornado.web import HTTPError

from typing import Dict

from illumidesk.authenticators.validator import LTI13LaunchValidator


def mock_lti13_claims() -> Dict[str, str]:
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
        'key2': 'value2',
        'key3': 'value3',
    }

    with pytest.raises(HTTPError):
        validator.validate_launch_request(fake_jws)


def test_validate_invalid_resource_link_request_claim_value():
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
    print(jws['https://purl.imsglobal.org/spec/lti/claim/roles'])

    assert validator.validate_launch_request(jws)
