import json
import jwt
import logging
import time
import urllib

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
        'exp': int(time.time()) + 600,
        'iat': int(time.time()),
        'jti': uuid.uuid4().hex
    }
    logger.debug('Getting lms access token with parameters %s' % token_params)
    token = jwt.encode(
        token_params,
        private_key,
        algorithm='RS256',
    )
    logger.debug('Obtaining token %s' % token)
    scope = scope or ' '.join([
        'https://purl.imsglobal.org/spec/lti-ags/scope/score',
        'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem',
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
        logger.info(e.response.body)
        raise
    logger.debug('Token response body is %s' % json.loads(resp.body))
    return json.loads(resp.body)
