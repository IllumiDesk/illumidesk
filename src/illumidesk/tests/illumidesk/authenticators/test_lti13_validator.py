import pytest

from tornado.web import HTTPError

from unittest.mock import patch

from illumidesk.authenticators.validator import LTI13LaunchValidator
from illumidesk.tests.factory import dummy_lti13_id_token
from illumidesk.tests.factory import factory_lti13_required_claims
from illumidesk.tests.factory import factory_empty_platform_jwks


@pytest.mark.asyncio
async def test_validator_jwt_verify_and_decode_invokes_retrieve_matching_jwk():
    """
    Does the validator jwt_verify_and_decode method invoke the retrieve_matching_jwk method?
    """
    validator = LTI13LaunchValidator()
    jwks_endoint = 'https://my.platform.domain/api/lti/security/jwks'
    with patch.object(
        LTI13LaunchValidator, '_retrieve_matching_jwk', return_value=factory_empty_platform_jwks()
    ) as mock_retrieve_matching_jwks:
        result = await validator.jwt_verify_and_decode(dummy_lti13_id_token, jwks_endoint, False)

    assert result is None


@pytest.mark.asyncio
async def test_validator_jwt_verify_and_decode_returns_none_with_no_retrieved_platform_keys():
    """
    Does the validator jwt_verify_and_decode method return None when no keys are returned from the
    retrieve_matching_jwk method?
    """
    validator = LTI13LaunchValidator()
    jwks_endoint = 'https://my.platform.domain/api/lti/security/jwks'
    with patch.object(
        LTI13LaunchValidator, '_retrieve_matching_jwk', return_value=factory_empty_platform_jwks()
    ) as mock_retrieve_matching_jwks:
        result = await validator.jwt_verify_and_decode(dummy_lti13_id_token, jwks_endoint, True)

    assert result is None


def test_validate_empty_roles_claim_value():
    """
    Is the JWT valid with an empty roles claim value?
    """
    validator = LTI13LaunchValidator()
    jws = factory_lti13_required_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/roles'] = ''

    assert validator.validate_launch_request(jws)


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
    jws = factory_lti13_required_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/message_type'] = 'FakeLinkRequest'

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_invalid_version_request_claim_value():
    """
    Is the JWT valid with an incorrect version claim?
    """
    validator = LTI13LaunchValidator()
    jws = factory_lti13_required_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/version'] = '1.0.0'

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_empty_deployment_id_request_claim_value():
    """
    Is the JWT valid with an empty deployment_id claim?
    """
    validator = LTI13LaunchValidator()
    jws = factory_lti13_required_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/deployment_id'] = ''

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_empty_target_link_uri_request_claim_value():
    """
    Is the JWT valid with an empty target link uri claim?
    """
    validator = LTI13LaunchValidator()
    jws = factory_lti13_required_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/target_link_uri'] = ''

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_empty_resource_link_id_request_claim_value():
    """
    Is the JWT valid with an empty resource request id uri claim?
    """
    validator = LTI13LaunchValidator()
    jws = factory_lti13_required_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/resource_link']['id'] = ''

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_empty_roles_claim_value():
    """
    Is the JWT valid with an empty roles claim value?
    """
    validator = LTI13LaunchValidator()
    jws = factory_lti13_required_claims()
    jws['https://purl.imsglobal.org/spec/lti/claim/roles'] = ''

    assert validator.validate_launch_request(jws)
