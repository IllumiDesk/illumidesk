import logging

from urllib.parse import quote
from urllib.parse import urlparse
from uuid import uuid4

from jupyterhub.handlers import BaseHandler

from oauthenticator.oauth2 import _serialize_state
from oauthenticator.oauth2 import OAuthLoginHandler
from oauthenticator.oauth2 import OAuthCallbackHandler
from oauthenticator.oauth2 import STATE_COOKIE_NAME

from tornado import web
from tornado.web import HTTPError

# from tornado.web import RequestHandler

from typing import Dict


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


class LTI13LoginHandler(OAuthLoginHandler):
    """
    Handles JupyterHub authentication requests according to the
    LTI 1.3 standard.
    """

    def get_state(self) -> Dict[str, str]:
        """
        Overrides OAuthLoginHandler.get_state() to get the user's
        next_url based on LTI's target link uri, also known as
        the lauch request url.

        The function uses tornado's RequestHandler to get arguments
        from the request.

        Returns:
          JupyterHub's next_url and state_id dict
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

    def post(self):
        """
        Handles LTI 1.3 authentication by building a dict with the required values
        and then redirecting the user to the callback URL using the redirect_uri
        that in turn uses the guess_callback_uri function from the oauthenticator.oauth2
        module.
        """
        login_hint = self.get_argument('login_hint')
        self.log.debug('Received login_hint: %s' % login_hint)
        lti_message_hint = self.get_argument('lti_message_hint')
        self.log.debug('Received lti_message_hint is %s' % lti_message_hint)
        client_id = self.get_argument('client_id')
        self.log.debug('Received client_id is %s' % client_id)
        nonce = self.get_argument('nonce')
        state = self.get_state()
        self.set_state_cookie(state)
        self.log.debug('State cookie set to %s' % state)
        redirect_uri = self.get_argument('redirect_uri')
        self.log.debug('Received redirect_uri: %s' % redirect_uri)
        self.authorize_redirect(
            client_id, lti_message_hint, login_hint, nonce, redirect_uri, state,
        )

    def authorize_redirect(
        self,
        prompt: str = 'none',
        response_mode: str = 'form_post',
        response_type: str = 'id_token',
        scope: str = 'openid',
        client_id: str = None,
        lti_message_hint: str = None,
        login_hint: str = None,
        nonce: str = None,
        redirect_uri: str = None,
        state: str = None,
    ) -> None:
        """
        Implements the OAuth2Mixin to to initiate the LTI 1.3 / OIDC login flow.
        Arguments are sent to the platform's authorization server for further processing.

        References:
        https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        http://www.imsglobal.org/spec/lti/v1p3/#additional-login-parameters-0
        
        Args:
          prompt: used to prompt user for reauthentication and consent, defaults to none
          response_mode: how the platform responds to the tool, defaults to form_post
          scope: oauth2 scope, defaults to 'openid'
          response_type: oauth2 response type, defaults to 'id_token'
          client_id: used to identify the tool's installation in a platform
          redirect_uri: endpoint specified during tool installation (callback url)
          extra_params: dictionary that contains extra parameters for oauth redirect
          
        """
        # handler = cast(RequestHandler, self)
        # use the first argument to set up dictionary
        args = {'prompt': prompt}
        args['response_mode'] = response_mode
        args['response_type'] = response_type
        args['scope'] = scope
        if not client_id:
            raise HTTPError(403, 'Missing client_id')
        args['client_id'] = self.get_argument('client_id')
        if not lti_message_hint:
            raise HTTPError(403, 'Missing lti_message_hint')
        args['lti_message_hint'] = self.get_argument('lti_message_hint')
        if not login_hint:
            raise HTTPError(403, 'Missing login_hint')
        args['login_hint'] = self.get_argument('login_hint')
        if not nonce:
            raise HTTPError(403, 'Missing nonce')
        args['nonce'] = self.get_argument('nonce')
        if not redirect_uri:
            raise HTTPError(403, 'Missing redirect_uri')
        args['redirect_uri'] = self.get_argument('redirect_uri')
        if not state:
            raise HTTPError(403, 'Missing redirect_uri')
        args['state'] = self.get_argument('state')
        url = self._OAUTH_AUTHORIZE_URL  # type: ignore
        # handler.redirect(url_concat(url, args))


class LTI13CallbackHandler(OAuthCallbackHandler):
    """
    LTI 1.3 call back handler
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
            raise web.HTTPError(403, 'User missing or null')
        self.redirect(self.get_next_url(user))
        self.log.debug('Redirecting user %s to %s' % (user.id, self.get_next_url(user)))
