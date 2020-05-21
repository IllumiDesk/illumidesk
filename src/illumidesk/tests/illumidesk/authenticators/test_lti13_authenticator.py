import pytest

from tornado.web import RequestHandler

from typing import Dict

from unittest.mock import Mock
from unittest.mock import patch

from illumidesk.authenticators.validator import LTI13LaunchValidator
from illumidesk.authenticators.authenticator import LTI13Authenticator

from illumidesk.tests.mocks import mock_handler


def mock_lti13_resource_link_request() -> Dict[str, str]:
    jws = {
        'https://purl.imsglobal.org/spec/lti/claim/message_type': 'LtiResourceLinkRequest',
        'https://purl.imsglobal.org/spec/lti/claim/version': '1.3.0',
        'https://purl.imsglobal.org/spec/lti/claim/resource_link': {
            'id': 'b81accac78543cb7cd239f3792bcfdc7c6efeadb',
            'description': None,
            'title': None,
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
        'https://purl.imsglobal.org/spec/lti/claim/target_link_uri': 'https://edu.example.com/hub',
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
            'name': 'IllumiDesk',
            'version': 'cloud',
            'product_family_code': 'canvas',
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
        'https://purl.imsglobal.org/spec/lti/claim/custom': {'email': 'foo@example.com'},
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
        'email': 'foo@example.com',
        'name': 'Foo Bar',
        'given_name': 'Foo',
        'family_name': 'Bar',
        'https://purl.imsglobal.org/spec/lti/claim/lis': {
            'person_sourcedid': None,
            'course_offering_sourcedid': None,
            'validation_context': None,
            'errors': {'errors': {}},
        },
        'https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice': {
            'context_memberships_url': 'https://illumidesk.instructure.com/api/lti/courses/147/names_and_roles',
            'service_versions': ['2.0',],  # noqa: E231
            'validation_context': None,
            'errors': {'errors': {}},
        },  # noqa: E231
    }
    return jws


id_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IjIwMjAtMDQtMDFUMDA6MDA6MDRaIn0.eyJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9tZXNzYWdlX3R5cGUiOiJMdGlSZXNvdXJjZUxpbmtSZXF1ZXN0IiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vdmVyc2lvbiI6IjEuMy4wIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vcmVzb3VyY2VfbGluayI6eyJpZCI6ImI4MWFjY2FjNzg1NDNjYjdjZDIzOWYzNzkyYmNmZGM3YzZlZmVhZGIiLCJkZXNjcmlwdGlvbiI6bnVsbCwidGl0bGUiOm51bGwsInZhbGlkYXRpb25fY29udGV4dCI6bnVsbCwiZXJyb3JzIjp7ImVycm9ycyI6e319fSwiYXVkIjoiMTI1OTAwMDAwMDAwMDAwMDcxIiwiYXpwIjoiMTI1OTAwMDAwMDAwMDAwMDcxIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vZGVwbG95bWVudF9pZCI6Ijg0NzpiODFhY2NhYzc4NTQzY2I3Y2QyMzlmMzc5MmJjZmRjN2M2ZWZlYWRiIiwiZXhwIjoxNTg5ODQzNDIxLCJpYXQiOjE1ODk4Mzk4MjEsImlzcyI6Imh0dHBzOi8vY2FudmFzLmluc3RydWN0dXJlLmNvbSIsIm5vbmNlIjoiMTI1Njg3MDE4NDM3Njg3MjI5NjIxNTg5ODM5ODIyIiwic3ViIjoiODE3MTkzNGItZjVlMi00ZjRlLWJkYmQtNmQ3OTg2MTViOTNlIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vdGFyZ2V0X2xpbmtfdXJpIjoiaHR0cHM6Ly9lZHUuZXhhbXBsZS5jb20vaHViIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vY29udGV4dCI6eyJpZCI6ImI4MWFjY2FjNzg1NDNjYjdjZDIzOWYzNzkyYmNmZGM3YzZlZmVhZGIiLCJsYWJlbCI6ImludHJvMTAxIiwidGl0bGUiOiJpbnRybzEwMSIsInR5cGUiOlsiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvY291cnNlI0NvdXJzZU9mZmVyaW5nIl0sInZhbGlkYXRpb25fY29udGV4dCI6bnVsbCwiZXJyb3JzIjp7ImVycm9ycyI6e319fSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vdG9vbF9wbGF0Zm9ybSI6eyJndWlkIjoic3JudXo2aDFVOGtPTW1FVHpvcVpUSmlQV3piUFhJWWtBVW5uQUo0dTpjYW52YXMtbG1zIiwibmFtZSI6IklsbHVtaURlc2siLCJ2ZXJzaW9uIjoiY2xvdWQiLCJwcm9kdWN0X2ZhbWlseV9jb2RlIjoiY2FudmFzIiwidmFsaWRhdGlvbl9jb250ZXh0IjpudWxsLCJlcnJvcnMiOnsiZXJyb3JzIjp7fX19LCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9sYXVuY2hfcHJlc2VudGF0aW9uIjp7ImRvY3VtZW50X3RhcmdldCI6ImlmcmFtZSIsImhlaWdodCI6NDAwLCJ3aWR0aCI6ODAwLCJyZXR1cm5fdXJsIjoiaHR0cHM6Ly9pbGx1bWlkZXNrLmluc3RydWN0dXJlLmNvbS9jb3Vyc2VzLzE0Ny9leHRlcm5hbF9jb250ZW50L3N1Y2Nlc3MvZXh0ZXJuYWxfdG9vbF9yZWRpcmVjdCIsImxvY2FsZSI6ImVuIiwidmFsaWRhdGlvbl9jb250ZXh0IjpudWxsLCJlcnJvcnMiOnsiZXJyb3JzIjp7fX19LCJsb2NhbGUiOiJlbiIsImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL3JvbGVzIjpbImh0dHA6Ly9wdXJsLmltc2dsb2JhbC5vcmcvdm9jYWIvbGlzL3YyL2luc3RpdHV0aW9uL3BlcnNvbiNTdHVkZW50IiwiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvbWVtYmVyc2hpcCNMZWFybmVyIiwiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvc3lzdGVtL3BlcnNvbiNVc2VyIl0sImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL2N1c3RvbSI6eyJlbWFpbCI6ImZvb0BleGFtcGxlLmNvbSJ9LCJlcnJvcnMiOnsiZXJyb3JzIjp7fX0sImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpLWFncy9jbGFpbS9lbmRwb2ludCI6eyJzY29wZSI6WyJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1hZ3Mvc2NvcGUvbGluZWl0ZW0iLCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1hZ3Mvc2NvcGUvbGluZWl0ZW0ucmVhZG9ubHkiLCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1hZ3Mvc2NvcGUvcmVzdWx0LnJlYWRvbmx5IiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGktYWdzL3Njb3BlL3Njb3JlIl0sImxpbmVpdGVtcyI6Imh0dHBzOi8vaWxsdW1pZGVzay5pbnN0cnVjdHVyZS5jb20vYXBpL2x0aS9jb3Vyc2VzLzE0Ny9saW5lX2l0ZW1zIiwidmFsaWRhdGlvbl9jb250ZXh0IjpudWxsLCJlcnJvcnMiOnsiZXJyb3JzIjp7fX19LCJwaWN0dXJlIjoiaHR0cHM6Ly9jYW52YXMuaW5zdHJ1Y3R1cmUuY29tL2ltYWdlcy9tZXNzYWdlcy9hdmF0YXItNTAucG5nIiwiZW1haWwiOiJmb29AZXhhbXBsZS5jb20iLCJuYW1lIjoiRm9vIEJhciIsImdpdmVuX25hbWUiOiJGb28iLCJmYW1pbHlfbmFtZSI6IkJhciIsImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL2xpcyI6eyJwZXJzb25fc291cmNlZGlkIjpudWxsLCJjb3Vyc2Vfb2ZmZXJpbmdfc291cmNlZGlkIjpudWxsLCJ2YWxpZGF0aW9uX2NvbnRleHQiOm51bGwsImVycm9ycyI6eyJlcnJvcnMiOnt9fX0sImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpLW5ycHMvY2xhaW0vbmFtZXNyb2xlc2VydmljZSI6eyJjb250ZXh0X21lbWJlcnNoaXBzX3VybCI6Imh0dHBzOi8vaWxsdW1pZGVzay5pbnN0cnVjdHVyZS5jb20vYXBpL2x0aS9jb3Vyc2VzLzE0Ny9uYW1lc19hbmRfcm9sZXMiLCJzZXJ2aWNlX3ZlcnNpb25zIjpbIjIuMCJdLCJ2YWxpZGF0aW9uX2NvbnRleHQiOm51bGwsImVycm9ycyI6eyJlcnJvcnMiOnt9fX19.LycKGp1Q0OIcO3XZqLubxk3_V_KzdNmDIaM9X84r7BI'


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_handler_get_argument():
    """
    Does the authenticator invoke the RequestHandler get_argument method?
    """
    authenticator = LTI13Authenticator()

    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(RequestHandler, 'get_argument', return_value=id_token.encode()) as mock_get_argument:
        authenticator = LTI13Authenticator()
        _ = await authenticator.authenticate(request_handler, None)

        assert mock_get_argument.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_jwt_verify_and_decode():
    """
    Does the authenticator invoke the LTI13Validator jwt_verify_and_decode method?
    """
    with patch.object(
        LTI13LaunchValidator, 'jwt_verify_and_decode', return_value=mock_lti13_resource_link_request()
    ) as mock_validator:
        authenticator = LTI13Authenticator()
        handler = Mock(spec=RequestHandler)
        handler.get_argument = lambda x, strip=True: id_token.encode() if x == 'id_token' else ''
        _ = await authenticator.authenticate(handler, None)

        assert mock_validator.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_validate_launch_request():
    """
    Does the authenticator invoke the LTI13Validator validate_launch_request method?
    """
    with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True) as mock_validator:
        authenticator = LTI13Authenticator()
        handler = Mock(spec=RequestHandler)
        handler.get_argument = lambda x, strip=True: id_token.encode() if x == 'id_token' else ''
        _ = await authenticator.authenticate(handler, None)

        assert mock_validator.called


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_valid_email():
    """
    Do we get a valid username when adding a valid email to the resource link request?
    """
    with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI13Authenticator()
        handler = Mock(spec=RequestHandler)
        handler.get_argument = lambda x, strip=True: id_token.encode() if x == 'id_token' else ''
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
        }
        assert result['name'] == expected['name']


@pytest.mark.asyncio
async def test_authenticator_returns_course_id_in_auth_state_with_valid_course_id():
    """
    Do we get a valid course_id when adding a valid course id to the resource link request?
    """
    with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI13Authenticator()
        handler = Mock(spec=RequestHandler)
        handler.get_argument = lambda x, strip=True: id_token.encode() if x == 'id_token' else ''
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
        }
        assert result['auth_state']['course_id'] == expected['auth_state']['course_id']


@pytest.mark.asyncio
async def test_authenticator_returns_user_role_in_auth_state_with_valid_user_role():
    """
    Do we get a valid use_role in the auth_state when adding a valid user role to the resource link request?
    """
    with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI13Authenticator()
        handler = Mock(spec=RequestHandler)
        handler.get_argument = lambda x, strip=True: id_token.encode() if x == 'id_token' else ''
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
        }
        assert result['auth_state']['user_role'] == expected['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_valid_user_role():
    """
    Do we get a valid use_role in the auth_state when adding a valid user role to the resource link request?
    """
    with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI13Authenticator()
        handler = Mock(spec=RequestHandler)
        handler.get_argument = lambda x, strip=True: id_token.encode() if x == 'id_token' else ''
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
        }
        assert result['auth_state']['user_role'] == expected['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_learner_role_in_auth_state_with_missing_user_role():
    """
    Do we set the learner role in the auth_state when setting a missing role in the resource link request?
    """
    with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True) and patch.object(
        LTI13LaunchValidator, 'validate_launch_request', return_value=mock_lti13_resource_link_request
    ):
        authenticator = LTI13Authenticator()
        handler = Mock(spec=RequestHandler)
        handler.get_argument = lambda x, strip=True: id_token.encode() if x == 'missing_role_id_token' else ''
        validator = Mock(spec=LTI13LaunchValidator)
        validator.jwt_verify_and_decode = lambda x, strip=True: id_token.encode() if x == 'id_token' else ''
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {'course_id': 'intro101', 'lms_user_id': 'foo', 'user_role': 'Learner',},  # noqa: E231
        }
        assert result['auth_state']['user_role'] == expected['auth_state']['user_role']
