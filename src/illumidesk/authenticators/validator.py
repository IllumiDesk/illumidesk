import json
import jwt
import time

from collections import OrderedDict

from josepy.jws import JWS
from josepy.jws import Header

from oauthlib.oauth1.rfc5849 import signature

from tornado.httpclient import AsyncHTTPClient
from tornado.web import HTTPError

from traitlets.config import LoggingConfigurable

from typing import Any
from typing import Dict

from .constants import LTI11_LAUNCH_PARAMS_REQUIRED
from .constants import LTI11_OAUTH_ARGS
from .constants import LTI13_REQUIRED_CLAIMS


class LTI11LaunchValidator(LoggingConfigurable):
    """
    This class closely mimics the jupyterhub/ltiauthenticator LTILaunchValidator
    base class. Inherits from the LoggingConfigurable traitlet to support logging.

    Allows JupyterHub to verify LTI 1.1 compatible requests as a tool
    provider (TP).

    For an instance of this class to work, you need to set the consumer key and
    shared secret key(s)/value(s) in `LTI11Authenticator` settings, which inherits
    from the ``ltiauthenticator.LTIAuthenticator`` class. The key/value pairs are
    set as are defined as a dict using the ``consumers`` attribute.

    Attributes:
      consumers: consumer key and shared secret key/value pair(s)
    """

    # Keep a class-wide, global list of nonces so we can detect & reject
    # replay attacks. This possibly makes this non-threadsafe, however.
    nonces = OrderedDict()

    def __init__(self, consumers):
        self.consumers = consumers

    def validate_launch_request(self, launch_url: str, headers: Dict[str, Any], args: Dict[str, Any],) -> bool:
        """
        Validate a given LTI 1.1 launch request. The arguments' k/v's are either
        required, recommended, or optional. The required/recommended/optional
        keys are defined as constants.

        Args:
          launch_url: URL (base_url + path) that receives the launch request,
            usually from a tool consumer.
          headers: HTTP headers included with the POST request
          args: the body sent to the launch url.

        Returns:
          True if the validation passes, False otherwise.

        Raises:
          HTTPError if a required argument is not inclued in the POST request.
        """
        # Ensure that required oauth_* body arguments are included in the request
        for param in LTI11_OAUTH_ARGS:
            if param not in args.keys():
                raise HTTPError(400, 'Required oauth arg %s not included in request' % param)
            if not args.get(param):
                raise HTTPError(400, 'Required oauth arg %s does not have a value' % param)

        # Ensure that consumer key is registered in in jupyterhub_config.py
        # LTI11Authenticator.consumers defined in parent class
        if args['oauth_consumer_key'] not in self.consumers:
            raise HTTPError(401, 'unknown oauth_consumer_key')

        # Ensure that required LTI 1.1 body arguments are included in the request
        for param in LTI11_LAUNCH_PARAMS_REQUIRED:
            if param not in args.keys():
                raise HTTPError(400, 'Required LTI arg %s not included in request' % param)
            if not args.get(param):
                raise HTTPError(400, 'Required LTI arg %s does not have a value' % param)

        # Inspiration to validate nonces/timestamps from OAuthlib
        # https://github.com/oauthlib/oauthlib/blob/master/oauthlib/oauth1/rfc5849/endpoints/base.py#L147
        if len(str(int(args['oauth_timestamp']))) != 10:
            raise HTTPError(401, 'Invalid timestamp size')
        try:
            ts = int(args['oauth_timestamp'])
        except ValueError:
            raise HTTPError(401, 'Timestamp must be an integer')
        else:
            # Reject timestamps that are older than 30 seconds
            if abs(time.time() - ts) > 30:
                raise HTTPError(
                    401,
                    'Timestamp given is invalid, differ from '
                    'allowed by over %s seconds.' % str(int(time.time() - ts)),
                )
            if ts in LTI11LaunchValidator.nonces and args['oauth_nonce'] in LTI11LaunchValidator.nonces[ts]:
                raise HTTPError(401, 'oauth_nonce + oauth_timestamp already used')
            LTI11LaunchValidator.nonces.setdefault(ts, set()).add(args['oauth_nonce'])

        # convert arguments dict back to a list of tuples for signature
        args_list = [(k, v) for k, v in args.items()]

        base_string = signature.signature_base_string(
            'POST',
            signature.base_string_uri(launch_url),
            signature.normalize_parameters(signature.collect_parameters(body=args_list, headers=headers)),
        )
        consumer_secret = self.consumers[args['oauth_consumer_key']]
        sign = signature.sign_hmac_sha1(base_string, consumer_secret, None)
        is_valid = signature.safe_string_equals(sign, args['oauth_signature'])
        self.log.debug('signature in request: %s' % args['oauth_signature'])
        self.log.debug('calculated signature: %s' % sign)
        if not is_valid:
            raise HTTPError(401, 'Invalid oauth_signature')

        return True


class LTI13LaunchValidator(LoggingConfigurable):
    """
    Allows JupyterHub to verify LTI 1.3 compatible requests as a tool (known as a tool
    provider with LTI 1.1).
    """

    async def _retrieve_matching_jwk(self, endpoint: str, verify: bool = True) -> Dict[str, str]:
        """
        Retrieves the matching cryptographic key from the platform as a
        JSON Web Key (JWK).

        Args:
          endpoint: platform endpoint
          token: jwt token
          verify: if true, validate certificate
        """
        client = AsyncHTTPClient()
        resp = await client.fetch(endpoint, validate_cert=verify)
        self.log.debug('Retrieving matching jwk %s' % json.loads(resp.body))
        return json.loads(resp.body)

    async def jwt_verify_and_decode(
        self, token: str, jwks: str, verify: bool = True, audience: str = None
    ) -> Dict[str, str]:
        """
        Decodes the JSON Web Token (JWT) sent from the platform. The JWT should contain claims
        that represent properties associated with the request. This method implicitly verifies the JWT's
        signature using the platform's public key.

        Args:
          token: token issued by the authorization server
          jwks: JSON web key (publick key)
          verify: verify whether or not to verify JWT when decoding. Defaults to True.
          audience: the platform's OAuth2 Audience (aud). This value usually coincides with the
            token endpoint for the platform (LMS) such as https://my.lms.domain/login/oauth2/token
        """
        if verify is False:
            self.log.debug('JWK verification is off, returning token %s' % jwt.decode(token, verify=False))
            return jwt.decode(token, verify=False)
        retrieved_jwks = await self._retrieve_matching_jwk(jwks, verify)
        jws = JWS.from_compact(bytes(token, 'utf-8'))
        self.log.debug('Retrieving matching jws %s' % jws)
        json_header = jws.signature.protected
        header = Header.json_loads(json_header)
        self.log.debug('Header from decoded jwt %s' % header)
        key = None
        for jwk in retrieved_jwks['keys']:
            if jwk['kid'] != header.kid:
                continue
            key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
            self.log.debug('Get keys from jwks dict  %s' % key)
        if key is None:
            self.log.debug('Key is None, returning None')
            return None
        self.log.debug('Returning decoded jwt with token %s key %s and verify %s' % (token, key, verify))
        return jwt.decode(token, key, verify, audience=audience)

    def validate_launch_request(self, jwt_decoded: Dict[str, Any],) -> bool:
        """
        Validates that a given LTI 1.3 launch request has the required and/or optional claims.
        The required claims are defined as constants.

        Args:
          jwt_decoded: decode JWT payload

        Returns:
          True if the validation passes, False otherwise.

        Raises:
          HTTPError if a required argument is not included in the request.
        """
        for claim, v in LTI13_REQUIRED_CLAIMS.items():
            if claim not in jwt_decoded.keys():
                raise HTTPError(400, 'Required claim %s not included in request' % claim)
        if jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/message_type'] != 'LtiResourceLinkRequest':
            raise HTTPError(400, 'Incorrect message type value')
        if jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/version'] != '1.3.0':
            raise HTTPError(400, 'Incorrect version value')
        if jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/deployment_id'] == '':
            raise HTTPError(400, 'Missing deployment_id value')
        if jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/resource_link']['id'] == '':
            raise HTTPError(400, 'Missing resource_link id value')
        if jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/target_link_uri'] == '':
            raise HTTPError(400, 'Missing target_link_uri value')

        return True
