import os
import json
import logging
import time

from hashlib import md5
from secrets import randbits
from uuid import uuid4
from urllib.parse import quote, urlparse

from Crypto.PublicKey import RSA

from jupyterhub.handlers import BaseHandler

from jwkest import long_to_base64

from oauthenticator.oauth2 import _serialize_state
from oauthenticator.oauth2 import guess_callback_uri
from oauthenticator.oauth2 import OAuthLoginHandler
from oauthenticator.oauth2 import OAuthCallbackHandler
from oauthenticator.oauth2 import STATE_COOKIE_NAME

from tornado import web
from tornado.auth import OAuth2Mixin

from .utils import LTIUtils

logger = logging.getLogger(__name__)


class LTI11AuthenticateHandler(BaseHandler):
    """
    LTI login handler obtained from jupyterhub/ltiauthenticator.

    If there's a custom parameter called 'next', will redirect user to
    that URL after authentication. Else, will send them to /home.
    """

    async def post(self):
        user = await self.login_user()  # noqa: F841
        self.redirect(self.get_body_argument('custom_next', self.get_next_url()))


class LTI13LoginHandler(OAuthLoginHandler, OAuth2Mixin):
    """
    Handles JupyterHub authentication requests according to the
    LTI 1.3 standard.
    """

    def post(self):
        """
        Handles LTI 1.3 authentication by building a dict with the
        required values and then redirecting the user to the callback
        URL using the redirect_uri that in turn uses the guess_callback_uri
        function from the oauthenticator.oauth2 module.
        """
        login_hint = self.get_argument('login_hint')
        self.log.debug('Login hint is %s' % login_hint)
        lti_message_hint = self.get_argument('lti_message_hint')
        self.log.debug('lti_message_hint is %s' % lti_message_hint)
        client_id = self.get_argument('client_id')
        self.log.debug('client_id is %s' % client_id)
        nonce = str(str(randbits(64)) + str(int(time.time())))
        state = self.get_state()
        self.set_state_cookie(state)
        self.log.debug('State cookie set to %s' % state)
        redirect_uri = guess_callback_uri('https', self.request.host, self.hub.server.base_url)
        self.log.debug('redirect_uri is %s' % redirect_uri)
        params = {
            'response_type': 'id_token',
            'scope': ['openid'],
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'extra_params': {
                'response_mode': 'form_post',
                'lti_message_hint': lti_message_hint,
                'prompt': 'none',
                'login_hint': login_hint,
                'state': state,
                'nonce': nonce,
            },
        }
        self.authorize_redirect(**params)

    def get_state(self):
        """
        Overrides OAuthLoginHandler.get_state() to get the user's
        next_url based on LTI's target link uri, also known as
        the lauch request url.

        The function uses tornado's RequestHandler to get arguments
        from the request.

        Returns:
          URL for state
        """
        next_url = self.get_argument('target_link_uri')
        self.log.debug('next_url is %s' % next_url)
        if next_url:
            next_url = next_url.replace('\\', quote('\\'))
            urlinfo = urlparse(next_url)
            next_url = urlinfo._replace(scheme='', netloc='', path='/' + urlinfo.path.lstrip('/'),).geturl()
        if self._state is None:
            self._state = _serialize_state({'state_id': uuid4().hex, 'next_url': next_url,})  # noqa: E231
            self.log.debug('state set to %s' % self._state)
        return self._state

    def set_state_cookie(self, state):
        """
        Sets a secure cookie. This method overrides tornado's RequestHandler
        set_state_cookie which uses the cookie_secret to encrypt cookie data.

        Args:
          state: state value from get_state()
        """
        self.log.debug('Setting cookie state')
        self.set_secure_cookie(STATE_COOKIE_NAME, state, expires_days=1, httponly=True)


class LTI13CallbackHandler(OAuthCallbackHandler):
    """
    LTI v1p3 call back handler
    """

    async def post(self):
        """
        Checks the user's state by validating the user's current
        cookie, logs in the user and then redirects the user to the
        registered next url.
        """
        self.check_state()
        user = await self.login_user()
        if user is None:
            raise web.HTTPError(403)
        self.redirect(self.get_next_url(user))
        self.log.debug('Redirecting user %s to %s' % (user.id, self.get_next_url(user)))


class LTI13JwksHandler(BaseHandler):
    """
    Class that handles JWKS for LTI 1.3
    """

    async def get(self):
        """
        Gets the JWKS keys/values which is used by LTI consumer
        tools to install the external tool (tool provider). Requires
        that the PRIVATE_KEY env var is set for the JupyterHub.
        """
        lti_utils = LTIUtils()
        self.set_header('Content-Type', 'application/json')
        if not os.environ.get('PRIVATE_KEY'):
            raise ValueError('PRIVATE_KEY environment variable not set')
        private_key = os.environ.get('PRIVATE_KEY')
        kid = md5(private_key.encode('utf-8')).hexdigest()
        self.log.debug('kid is %s' % kid)
        public_key = RSA.importKey(private_key).publickey()
        self.log.debug('public_key is %s' % public_key)
        # get the origin protocol
        protocol = lti_utils.get_client_protocol(self)
        self.log.debug('Origin protocol is: %s' % protocol)
        # build the full target link url value required for the jwks endpoint
        target_link_url = f'{protocol}://{self.request.host}/hub'
        self.log.debug('Target link url is: %s' % target_link_url)
        keys = {
            'title': 'IllumiDesk',
            'scopes': [
                'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem',
                'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly',
                'https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly',
                'https://purl.imsglobal.org/spec/lti-ags/scope/score',
                'https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly',
                'https://canvas.instructure.com/lti/public_jwk/scope/update',
                'https://canvas.instructure.com/lti/data_services/scope/create',
                'https://canvas.instructure.com/lti/data_services/scope/show',
                'https://canvas.instructure.com/lti/data_services/scope/update',
                'https://canvas.instructure.com/lti/data_services/scope/list',
                'https://canvas.instructure.com/lti/data_services/scope/destroy',
                'https://canvas.instructure.com/lti/data_services/scope/list_event_types',
                'https://canvas.instructure.com/lti/feature_flags/scope/show',
                'https://canvas.instructure.com/lti/account_lookup/scope/show',
            ],
            'extensions': [
                {
                    'platform': 'canvas.instructure.com',
                    'settings': {
                        'platform': 'canvas.instructure.com',
                        'placements': [
                            {
                                'placement': 'course_navigation',
                                'message_type': 'LtiResourceLinkRequest',
                                'windowTarget': '_blank',
                                'target_link_uri': target_link_url,
                                'custom_fields': {'email': '$Person.email.primary'},
                            },
                            {
                                'placement': 'assignment_selection',
                                'message_type': 'LtiResourceLinkRequest',
                                'target_link_uri': target_link_url,
                            },
                        ],
                    },
                    'privacy_level': 'public',
                }
            ],
            'public_jwk': {
                'n': long_to_base64(public_key.n),
                'e': long_to_base64(public_key.e),
                'alg': 'RS256',
                'kid': kid,
                'kty': 'RSA',
                'use': 'sig',
            },
            'description': 'illumidesk lti tool',
            'custom_fields': {'email': '$Person.email.primary'},
            'public_jwk_url': f'{target_link_url}/jwks',
            'target_link_uri': target_link_url,
            'oidc_initiation_url': f'{target_link_url}/oauth_login',
        }
        self.write(json.dumps(keys))
