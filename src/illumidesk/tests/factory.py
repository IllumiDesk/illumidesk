import secrets
import time

from oauthlib.oauth1.rfc5849 import signature

from typing import Dict

from illumidesk.authenticators.utils import LTIUtils


def factory_lti11_args(oauth_consumer_key: str, oauth_consumer_secret: str,) -> Dict[str, str]:

    utils = LTIUtils()
    oauth_timestamp = str(int(time.time()))
    oauth_nonce = secrets.token_urlsafe(32)
    extra_args = {'my_key': 'this_value'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    launch_url = 'http://jupyterhub/hub/lti/launch'
    args = {
        'lti_message_type': 'basic-lti-launch-request',
        'lti_version': 'LTI-1p0'.encode(),
        'resource_link_id': '88391-e1919-bb3456',
        'oauth_consumer_key': oauth_consumer_key,
        'oauth_timestamp': str(int(oauth_timestamp)),
        'oauth_nonce': str(oauth_nonce),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_callback': 'about:blank',
        'oauth_version': '1.0',
        'user_id': '123123123',
    }

    args.update(extra_args)

    base_string = signature.signature_base_string(
        'POST',
        signature.base_string_uri(launch_url),
        signature.normalize_parameters(signature.collect_parameters(body=args, headers=headers)),
    )

    args['oauth_signature'] = signature.sign_hmac_sha1(base_string, oauth_consumer_secret, None)

    return args


dummy_lti13_id_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IjIwMjAtMDQtMDFUMDA6MDA6MDRaIn0.eyJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9tZXNzYWdlX3R5cGUiOiJMdGlSZXNvdXJjZUxpbmtSZXF1ZXN0IiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vdmVyc2lvbiI6IjEuMy4wIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vcmVzb3VyY2VfbGluayI6eyJpZCI6ImI4MWFjY2FjNzg1NDNjYjdjZDIzOWYzNzkyYmNmZGM3YzZlZmVhZGIiLCJkZXNjcmlwdGlvbiI6bnVsbCwidGl0bGUiOm51bGwsInZhbGlkYXRpb25fY29udGV4dCI6bnVsbCwiZXJyb3JzIjp7ImVycm9ycyI6e319fSwiYXVkIjoiMTI1OTAwMDAwMDAwMDAwMDcxIiwiYXpwIjoiMTI1OTAwMDAwMDAwMDAwMDcxIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vZGVwbG95bWVudF9pZCI6Ijg0NzpiODFhY2NhYzc4NTQzY2I3Y2QyMzlmMzc5MmJjZmRjN2M2ZWZlYWRiIiwiZXhwIjoxNTg5ODQzNDIxLCJpYXQiOjE1ODk4Mzk4MjEsImlzcyI6Imh0dHBzOi8vY2FudmFzLmluc3RydWN0dXJlLmNvbSIsIm5vbmNlIjoiMTI1Njg3MDE4NDM3Njg3MjI5NjIxNTg5ODM5ODIyIiwic3ViIjoiODE3MTkzNGItZjVlMi00ZjRlLWJkYmQtNmQ3OTg2MTViOTNlIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vdGFyZ2V0X2xpbmtfdXJpIjoiaHR0cHM6Ly9lZHUuZXhhbXBsZS5jb20vaHViIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vY29udGV4dCI6eyJpZCI6ImI4MWFjY2FjNzg1NDNjYjdjZDIzOWYzNzkyYmNmZGM3YzZlZmVhZGIiLCJsYWJlbCI6ImludHJvMTAxIiwidGl0bGUiOiJpbnRybzEwMSIsInR5cGUiOlsiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvY291cnNlI0NvdXJzZU9mZmVyaW5nIl0sInZhbGlkYXRpb25fY29udGV4dCI6bnVsbCwiZXJyb3JzIjp7ImVycm9ycyI6e319fSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vdG9vbF9wbGF0Zm9ybSI6eyJndWlkIjoic3JudXo2aDFVOGtPTW1FVHpvcVpUSmlQV3piUFhJWWtBVW5uQUo0dTpjYW52YXMtbG1zIiwibmFtZSI6IklsbHVtaURlc2siLCJ2ZXJzaW9uIjoiY2xvdWQiLCJwcm9kdWN0X2ZhbWlseV9jb2RlIjoiY2FudmFzIiwidmFsaWRhdGlvbl9jb250ZXh0IjpudWxsLCJlcnJvcnMiOnsiZXJyb3JzIjp7fX19LCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9sYXVuY2hfcHJlc2VudGF0aW9uIjp7ImRvY3VtZW50X3RhcmdldCI6ImlmcmFtZSIsImhlaWdodCI6NDAwLCJ3aWR0aCI6ODAwLCJyZXR1cm5fdXJsIjoiaHR0cHM6Ly9pbGx1bWlkZXNrLmluc3RydWN0dXJlLmNvbS9jb3Vyc2VzLzE0Ny9leHRlcm5hbF9jb250ZW50L3N1Y2Nlc3MvZXh0ZXJuYWxfdG9vbF9yZWRpcmVjdCIsImxvY2FsZSI6ImVuIiwidmFsaWRhdGlvbl9jb250ZXh0IjpudWxsLCJlcnJvcnMiOnsiZXJyb3JzIjp7fX19LCJsb2NhbGUiOiJlbiIsImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL3JvbGVzIjpbImh0dHA6Ly9wdXJsLmltc2dsb2JhbC5vcmcvdm9jYWIvbGlzL3YyL2luc3RpdHV0aW9uL3BlcnNvbiNTdHVkZW50IiwiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvbWVtYmVyc2hpcCNMZWFybmVyIiwiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvc3lzdGVtL3BlcnNvbiNVc2VyIl0sImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL2N1c3RvbSI6eyJlbWFpbCI6ImZvb0BleGFtcGxlLmNvbSJ9LCJlcnJvcnMiOnsiZXJyb3JzIjp7fX0sImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpLWFncy9jbGFpbS9lbmRwb2ludCI6eyJzY29wZSI6WyJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1hZ3Mvc2NvcGUvbGluZWl0ZW0iLCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1hZ3Mvc2NvcGUvbGluZWl0ZW0ucmVhZG9ubHkiLCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1hZ3Mvc2NvcGUvcmVzdWx0LnJlYWRvbmx5IiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGktYWdzL3Njb3BlL3Njb3JlIl0sImxpbmVpdGVtcyI6Imh0dHBzOi8vaWxsdW1pZGVzay5pbnN0cnVjdHVyZS5jb20vYXBpL2x0aS9jb3Vyc2VzLzE0Ny9saW5lX2l0ZW1zIiwidmFsaWRhdGlvbl9jb250ZXh0IjpudWxsLCJlcnJvcnMiOnsiZXJyb3JzIjp7fX19LCJwaWN0dXJlIjoiaHR0cHM6Ly9jYW52YXMuaW5zdHJ1Y3R1cmUuY29tL2ltYWdlcy9tZXNzYWdlcy9hdmF0YXItNTAucG5nIiwiZW1haWwiOiJmb29AZXhhbXBsZS5jb20iLCJuYW1lIjoiRm9vIEJhciIsImdpdmVuX25hbWUiOiJGb28iLCJmYW1pbHlfbmFtZSI6IkJhciIsImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL2xpcyI6eyJwZXJzb25fc291cmNlZGlkIjpudWxsLCJjb3Vyc2Vfb2ZmZXJpbmdfc291cmNlZGlkIjpudWxsLCJ2YWxpZGF0aW9uX2NvbnRleHQiOm51bGwsImVycm9ycyI6eyJlcnJvcnMiOnt9fX0sImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpLW5ycHMvY2xhaW0vbmFtZXNyb2xlc2VydmljZSI6eyJjb250ZXh0X21lbWJlcnNoaXBzX3VybCI6Imh0dHBzOi8vaWxsdW1pZGVzay5pbnN0cnVjdHVyZS5jb20vYXBpL2x0aS9jb3Vyc2VzLzE0Ny9uYW1lc19hbmRfcm9sZXMiLCJzZXJ2aWNlX3ZlcnNpb25zIjpbIjIuMCJdLCJ2YWxpZGF0aW9uX2NvbnRleHQiOm51bGwsImVycm9ycyI6eyJlcnJvcnMiOnt9fX19.mtOYCPFyYcO6dbze4W_yd8hflSzsXhG6NnHhe9lVsdE'


def factory_lti13_required_claims() -> Dict[str, str]:
    """
    Valid json after decoding JSON Web Token (JWT) that only contains required fields.
    """
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


def factory_lti13_resource_link_request() -> Dict[str, str]:
    """
    Return valid json after decoding JSON Web Token (JWT) for resource link launch (core).
    """
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


def factory_platform_jwks():
    """
    Valid response when retrieving jwks from the platform.
    """
    jwks = {
        'keys': [
            {
                'kty': 'RSA',
                'e': 'AQAB',
                'n': 'sBrymOqJsg3huJMJmmYi7kSQX5IPPFJokfZaFPCM87TDBtjvV_ha_i_wJYDGoiqM3GKY-h1PditDxpMrqUOwKoIYXYySKurdAQr_G2pmkkdFtX0FDclgzjJyioElpgzrZdgy4y5TaW-HOOCaW7fFFOArkCkwqdAdxXRH4daLQCX0QyAPbgZPigsWbMm9DnQlBYIfkDVAf0kmiOvWsYOvuEMbapgZC5meW6XcNRQ2goEp6RJWF5SQ0ZTI64rxFG2FiGpqF4LyzgtP1th4qBKMTyKFfiHn0CA_LBIaZ90_htR6onTKgYr8v4TREJkdLyu7tyrSZjfUYCTdzkLFT9_dXQ',
                'kid': '2020-03-01T00:00:01Z',
                'alg': 'RS256',
                'use': 'sig',
            },
            {
                'kty': 'RSA',
                'e': 'AQAB',
                'n': '7AugnfFImg9HWNN1gfp-9f0Qx26ctPMVGj4BmKdknP2wnVWQPn7jvYl6J0H7YZY40adSePU-urJ2ICQnVyJjKu9DPNOvWanB-hG96zhf_6wsU8rZJhXwfJzM-K7xhd7f0pf0VFG7HZAJXFazoPkCTLpdQ_daNVp7jklhz2qzBe0Y_cIZaCqfAWMI7M046kYKkvk87rPkwi75O3sOqF7GmOIWCHqNzt3p69gPeYOirin9XeAEL9ZmTwgtVHSXM8W1sLCnTEukRLuuAZzTjC79B7TwEqDu5kXI7MuOHOueX3ePKjulXwRDVxK4JyuT0XPBe6xrFbh9hXBK9SB3XY33mw',
                'kid': '2020-04-01T00:00:04Z',
                'alg': 'RS256',
                'use': 'sig',
            },
            {
                'kty': 'RSA',
                'e': 'AQAB',
                'n': 'x5bJTy70O2XAMGVYq7ahfHZC6yovIfrH9pglFare2icDKVGA7u-9Fdruuma4lwwhRg6d7H3avZLY392zJKJByVkjNEfl0tszhbJ99jWoIzhvPNlk0_tCo1_9oCGEjZgh1wB8wVJIDm-Rt6ar5JwYNBGqPXbjWZTVRm5w9GccqLuK7Bc9RBecmU-WI1_pbWyz0T2I-9kn39K0u4Xhv3zTrZg_mkGsTNsVpBKkSSlHJnxsxq2_0v6TYNtzVmp2s7G11V3Ftp1gRQNaZcP2cEKISTip_Zj-bp63n8LaqH52Go1Jt7d1YFUSVth2OeWg4PURel8RIW5d0XwyaVVGbDMR2Q',
                'kid': '2020-05-01T00:00:01Z',
                'alg': 'RS256',
                'use': 'sig',
            },
        ]
    }
    return jwks


def factory_empty_platform_jwks():
    """
    Empty response when retrieving jwks from the platform.
    """
    jwks = {'keys': [{},]}  # noqa: E231
    return jwks
