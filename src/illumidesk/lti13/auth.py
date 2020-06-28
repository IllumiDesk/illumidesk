import json
import jwt
import logging
import pem
import os
import time
import urllib

from Crypto.PublicKey import RSA
from jwcrypto.jwk import JWK
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClientError
import uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def get_lms_access_token(token_endpoint: str, private_key_path: str, client_id: str, scope=None) -> str:
    """
    Gets an access token from the LMS Token endpoint by using the private key (pem format) and client id

    Args:
        token_endpoint: The url that will be used to make the request
        private_key_path: specify where the pem is
        client_id: For LTI 1.3 the Client ID that was obtained with the tool setup
    
    Returns:
        A json with the token value
    """
    token_params = {
        'iss': client_id,
        'sub': client_id,
        'aud': token_endpoint,
        'iat': int(time.time()) - 5,
        'exp': int(time.time()) + 60,
        'jti': str(uuid.uuid4()),
    }
    logger.debug('Getting lms access token with parameters %s' % token_params)
    # get the pem-encoded content
    private_key = get_pem_text_from_file(private_key_path)

    headers = get_headers_to_jwt_encode(private_key)

    token = jwt.encode(token_params, private_key, algorithm='RS256', headers=headers)
    logger.debug('Obtaining token %s' % token)
    scope = scope or ' '.join(
        [
            'https://purl.imsglobal.org/spec/lti-ags/scope/score',
            'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem',
            "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
            'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly',
        ]
    )
    logger.debug('Scope is %s' % scope)
    params = {
        'grant_type': 'client_credentials',
        'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
        'client_assertion': token.decode(),
        'scope': scope,
    }
    logger.debug('OAuth parameters are %s' % params)
    client = AsyncHTTPClient()
    body = urllib.parse.urlencode(params)
    try:
        resp = await client.fetch(token_endpoint, method='POST', body=body, headers=None)
    except HTTPClientError as e:
        logger.info(f'Error by obtaining a token with lms. Detail: {e.response.body if e.response else e.message}')
        raise
    logger.debug('Token response body is %s' % json.loads(resp.body))
    return json.loads(resp.body)


def get_jwk(public_key):
    jwk_obj = JWK.from_pem(public_key)
    public_jwk = json.loads(jwk_obj.export_public())
    public_jwk['alg'] = 'RS256'
    public_jwk['use'] = 'sig'
    return public_jwk


def get_headers_to_jwt_encode(private_key_text: str) -> dict:
    """
    Helper method that gets the dict headers to use in jwt.encode method

    Args:
        private_key_text: The PEM-Encoded content as text
    Returns: A dict if the publickey can be exported or None otherwise
    """
    public_key = RSA.importKey(private_key_text).publickey().exportKey()
    headers = None
    if public_key:
        jwk = get_jwk(public_key)
        headers = {'kid': jwk.get('kid')} if jwk else None

    return headers


def get_pem_text_from_file(private_key_path: str) -> str:
    """
    Parses the pem file to get its value as unicode text
    """
    # check the pem permission
    if not os.access(private_key_path, os.R_OK):
        raise PermissionError()
    # parse file generates a list of PEM objects
    certs = pem.parse_file(private_key_path)
    if not certs:
        raise Exception('Invalid pem file.')

    return certs[0].as_text()
