import logging
import time

from secrets import randbits
from urllib.parse import quote
from urllib.parse import urlparse
from uuid import uuid4

from jupyterhub.handlers import BaseHandler

from oauthenticator.oauth2 import _serialize_state
from oauthenticator.oauth2 import guess_callback_uri
from oauthenticator.oauth2 import OAuthLoginHandler
from oauthenticator.oauth2 import OAuthCallbackHandler
from oauthenticator.oauth2 import STATE_COOKIE_NAME

from tornado import web
from tornado.auth import OAuth2Mixin

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


class LTI13LoginHandler(OAuthLoginHandler, OAuth2Mixin):
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
