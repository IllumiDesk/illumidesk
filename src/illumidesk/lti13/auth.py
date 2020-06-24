import json
import jwt
import logging
import time
import urllib

from Crypto.PublicKey import RSA
from jwcrypto.jwk import JWK
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClientError
import uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def get_lms_access_token(token_endpoint, private_key, client_id, scope=None):
    token_params = {
        'iss': client_id,
        'sub': client_id,
        'aud': token_endpoint,
        'iat': int(time.time()) - 5,
        'exp': int(time.time()) + 60,
        'jti': str(uuid.uuid4())
    }
    logger.debug('Getting lms access token with parameters %s' % token_params)
    public_key = RSA.importKey(private_key).publickey().exportKey()
    headers = None
    if public_key:
        jwk = get_jwk(public_key)
        headers = {'kid': jwk.get('kid')} if jwk else None
    
    token = jwt.encode(
        token_params,
        private_key,
        algorithm='RS256',
        headers = headers
    )
    logger.debug('Obtaining token %s' % token)
    scope = scope or ' '.join([
        'https://purl.imsglobal.org/spec/lti-ags/scope/score',
        'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem',
        "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
        'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly'
    ])
    logger.debug('Scope is %s' % scope)
    params = {
        'grant_type': 'client_credentials',
        'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
        'client_assertion': token.decode(),
        'scope': scope
    }
    logger.debug('OAuth parameters are %s' % params)
    client = AsyncHTTPClient()
    body = urllib.parse.urlencode(params)
    try:
        resp = await client.fetch(token_endpoint, method='POST', body=body, headers=None)
    except HTTPClientError as e:
        logger.info(f'Error by obtaining a token with lms. Detail: {e.response.body}')
        raise
    logger.debug('Token response body is %s' % json.loads(resp.body))
    return json.loads(resp.body)


def get_jwk(public_key):
    jwk_obj = JWK.from_pem(public_key)
    public_jwk = json.loads(jwk_obj.export_public())
    public_jwk['alg'] = 'RS256'
    public_jwk['use'] = 'sig'
    return public_jwk