import logging
import hashlib
import os

from jupyterhub.handlers import BaseHandler

from oauthenticator.oauth2 import guess_callback_uri
from oauthenticator.oauth2 import OAuthLoginHandler
from oauthenticator.oauth2 import OAuthCallbackHandler

from tornado.httputil import url_concat
from tornado.web import HTTPError
from tornado.web import RequestHandler

from typing import cast

from illumidesk.authenticators.validator import LTI13LaunchValidator
from illumidesk.authenticators.utils import LTIUtils


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

    def authorize_redirect(
        self,
        client_id: str = None,
        login_hint: str = None,
        lti_message_hint: str = None,
        nonce: str = None,
        redirect_uri: str = None,
        state: str = None,
    ) -> None:
        """
        Overrides the OAuth2Mixin.authorize_redirect method to to initiate the LTI 1.3 / OIDC
        login flow. Arguments are redirected to the platform's authorization url for further
        processing.

        References:
        https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        http://www.imsglobal.org/spec/lti/v1p3/#additional-login-parameters-0
        
        Args:
          client_id: used to identify the tool's installation with a platform
          redirect_uri: redirect url specified during tool installation (callback url)
          login_hint: opaque value used by the platform for user identity
          lti_message_hint: signed JWT which contains information needed to perform the
            launch including issuer, user and context information
          nonce: unique value sent to allow recipients to protect themselves against replay attacks
          state: opaque value for the platform to maintain state between the request and
            callback and provide Cross-Site Request Forgery (CSRF) mitigation.
        """
        handler = cast(RequestHandler, self)
        args = {'response_type': 'id_token'}
        args['scope'] = 'openid'
        if redirect_uri is not None:
            args['redirect_uri'] = redirect_uri
        if client_id is not None:
            args['client_id'] = client_id
        extra_params = {'extra_params': {}}
        extra_params['response_mode'] = 'form_post'
        extra_params['prompt'] = 'none'
        if login_hint is not None:
            extra_params['login_hint'] = login_hint
        if lti_message_hint is not None:
            extra_params['lti_message_hint'] = lti_message_hint
        if state is not None:
            extra_params['state'] = state
        if nonce is not None:
            extra_params['nonce'] = nonce
        args.update(extra_params)
        url = os.environ.get('LTI13_AUTHORIZE_URL')
        if not url:
            raise EnvironmentError('LTI13_AUTHORIZE_URL env var is not set')
        handler.redirect(url_concat(url, args))

    def post(self):
        """
        Validates required login arguments sent from platform and then uses the authorize_redirect() method
        to redirect users to the authorization url.
        """
        lti_utils = LTIUtils()
        validator = LTI13LaunchValidator()
        args = lti_utils.convert_request_to_dict(self.request.arguments)
        self.log.debug('Initial login request args are %s' % args)
        if validator.validate_login_request(args):
            login_hint = args['login_hint']
            self.log.debug('login_hint is %s' % login_hint)
            lti_message_hint = args['lti_message_hint']
            self.log.debug('lti_message_hint is %s' % lti_message_hint)
            client_id = args['client_id']
            self.log.debug('client_id is %s' % client_id)
            redirect_uri = guess_callback_uri('https', self.request.host, self.hub.server.base_url)
            self.log.info('redirect_uri: %r', redirect_uri)
            state = self.get_state()
            self.set_state_cookie(state)
            # TODO: validate that received nonces haven't been received before
            # and that they are within the time-based tolerance window
            nonce_raw = hashlib.sha256(state.encode())
            nonce = nonce_raw.hexdigest()
            self.authorize_redirect(
                client_id=client_id,
                login_hint=login_hint,
                lti_message_hint=lti_message_hint,
                nonce=nonce,
                redirect_uri=redirect_uri,
                state=state,
            )


class LTI13CallbackHandler(OAuthCallbackHandler):
    """
    LTI 1.3 call back handler
    """

    async def post(self):
        """
        Overrides the upstream get handler with it's standard implementation.
        """
        self.check_state()
        user = await self.login_user()
        if user is None:
            raise HTTPError(403, 'User missing or null')
        self.redirect(self.get_next_url(user))
        self.log.debug('Redirecting user %s to %s' % (user.id, self.get_next_url(user)))
