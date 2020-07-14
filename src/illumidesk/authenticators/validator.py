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

from .constants import ILLUMIDESK_LTI13_REQUIRED_CLAIMS
from .constants import LTI11_LAUNCH_PARAMS_REQUIRED
from .constants import LTI11_OAUTH_ARGS
from .constants import LTI13_LOGIN_REQUEST_ARGS


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
                raise HTTPError(400, 'Required LTI 1.1 arg arg %s not included in request' % param)
            if not args.get(param):
                raise HTTPError(400, 'Required LTI 1.1 arg arg %s does not have a value' % param)

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

    async def _retrieve_matching_jwk(self, endpoint: str, header_kid: str, verify: bool = True) -> Any:
        """
        Retrieves the matching cryptographic key from the platform as a
        JSON Web Key (JWK).

        Args:
          endpoint: platform jwks endpoint
          header_kid: the kid received within the id_token
          verify: if true, validate certificate
        """
        client = AsyncHTTPClient()
        resp = await client.fetch(endpoint, validate_cert=verify)
        platform_jwks = json.loads(resp.body)
        self.log.debug('Retrieved jwks from lms platform %s' % platform_jwks)

        if not platform_jwks or 'keys' not in platform_jwks:
            raise ValueError('Platform endpoint returned an empty jwks')

        key = None
        for jwk in platform_jwks['keys']:
            if jwk['kid'] != header_kid:
                continue
            key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
            self.log.debug('Get keys from jwks dict  %s' % key)
        if key is None:
            error_msg = f'There is not a key matching in the platform jwks for the jwt received. kid: {header_kid}'
            self.log.debug(error_msg)
            raise ValueError(error_msg)

        return key

    async def jwt_verify_and_decode(
        self, id_token: str, jwks_endpoint: str, verify: bool = True, audience: str = None
    ) -> Dict[str, str]:
        """
        Decodes the JSON Web Token (JWT) sent from the platform. The JWT should contain claims
        that represent properties associated with the request. This method implicitly verifies the JWT's
        signature using the platform's public key.

        Args:
          id_token: JWT token issued by the platform
          jwks_endpoint: JSON web key (publick key) endpoint
          verify: verify whether or not to verify JWT when decoding. Defaults to True.
          audience: the platform's OAuth2 Audience (aud). This value usually coincides with the
            token endpoint for the platform (LMS) such as https://my.lms.domain/login/oauth2/token
        """
        if verify is False:
            self.log.debug('JWK verification is off, returning token %s' % jwt.decode(id_token, verify=False))
            return jwt.decode(id_token, verify=False)

        jws = JWS.from_compact(id_token)
        self.log.debug('Retrieving matching jws %s' % jws)
        json_header = jws.signature.protected
        header = Header.json_loads(json_header)
        self.log.debug('Header from decoded jwt %s' % header)

        key_from_jwks = await self._retrieve_matching_jwk(jwks_endpoint, verify, header.kid)
        self.log.debug('Returning decoded jwt with token %s key %s and verify %s' % (id_token, key_from_jwks, verify))

        return jwt.decode(id_token, key=key_from_jwks, verify=False, audience=audience)

    def validate_launch_request(self, jwt_decoded: Dict[str, Any],) -> bool:
        """
        Validates that a given LTI 1.3 launch request has the required required claims The
        required claims combine the required claims according to the LTI 1.3 standard and the
        required claims for this setup to work properly, which are obtaind from the LTI 1.3 standard
        optional claims and LIS optional claims.

        The required claims are defined as constants.

        Args:
          jwt_decoded: decode JWT payload

        Returns:
          True if the validation passes, False otherwise.

        Raises:
          HTTPError if a required claim is not included in the dictionary or if the message_type and/or
          version claims do not have the correct value.
        """
        for claim, v in ILLUMIDESK_LTI13_REQUIRED_CLAIMS.items():
            if claim not in jwt_decoded.keys():
                raise HTTPError(400, 'Required claim %s not included in request' % claim)
            if (
                'https://purl.imsglobal.org/spec/lti/claim/message_type' in jwt_decoded.keys()
                and jwt_decoded.get('https://purl.imsglobal.org/spec/lti/claim/message_type')
                != 'LtiResourceLinkRequest'
            ):
                raise HTTPError(400, 'Incorrect value %s for message type claim' % v)
            if (
                'https://purl.imsglobal.org/spec/lti/claim/version' in jwt_decoded.keys()
                and jwt_decoded.get('https://purl.imsglobal.org/spec/lti/claim/version') != '1.3.0'
            ):
                raise HTTPError(400, 'Incorrect value %s for version claim' % v)
            if (
                'https://purl.imsglobal.org/spec/lti/claim/resource_link' in jwt_decoded.keys()
                and jwt_decoded.get('https://purl.imsglobal.org/spec/lti/claim/resource_link').get('id') == ''
            ):
                raise HTTPError(400, 'Incorrect value %s for message type claim' % v)
            if (
                'https://purl.imsglobal.org/spec/lti/claim/context' in jwt_decoded.keys()
                and jwt_decoded.get('https://purl.imsglobal.org/spec/lti/claim/context').get('label') == ''
            ):
                raise HTTPError(400, 'Missing course context label %s for claim' % claim)
        return True

    def validate_login_request(self, args: Dict[str, Any]) -> bool:
        """
        Validates step 1 of authentication request.
        
        Args:
          args: dictionary that represents keys/values sent in authentication request
        
        Returns:
          True if the validation is ok, false otherwise
        """
        for param in LTI13_LOGIN_REQUEST_ARGS:
            if param not in args.keys():
                raise HTTPError(400, 'Required LTI 1.3 arg %s not included in request' % param)
            if not args.get(param):
                raise HTTPError(400, 'Required LTI 1.3 arg %s does not have a value' % param)
        return True
