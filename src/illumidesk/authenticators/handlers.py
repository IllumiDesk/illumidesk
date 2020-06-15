import logging
import hashlib
import os

from jupyterhub.handlers import BaseHandler

from oauthenticator.oauth2 import OAuthLoginHandler
from oauthenticator.oauth2 import OAuthCallbackHandler

from tornado.httputil import url_concat
from tornado.web import HTTPError
from tornado.web import RequestHandler

from tornado import web
from tornado.web import HTTPError

<<<<<<< HEAD
from typing import cast
=======
# from tornado.web import RequestHandler
>>>>>>> 9cb6ef6... fix merge conflicts

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
            extra_params['state'] = (state,)
        if nonce is not None:
            extra_params['nonce'] = (nonce,)
        args.update(extra_params)
        url = os.environ.get('LTI13_AUTHORIZE_URL')
        if not url:
            raise EnvironmentError('LTI13_AUTHORIZE_URL env var is not set')
        handler.redirect(url_concat(url, args))

    def post(self):
        """
        Validates required login arguments sent from platform and then uses the authorize_redirect() to redirect users to the authorization url.
        """
        lti_utils = LTIUtils()
        validator = LTI13LaunchValidator()
        args = lti_utils.convert_request_to_dict(self.request.arguments)
        if validator.validate_authentication_request(args):
            login_hint = args['login_hint']
            self.log.debug('login_hint is %s' % login_hint)
            lti_message_hint = args['lti_message_hint']
            self.log.debug('lti_message_hint is %s' % lti_message_hint)
            client_id = args['client_id']
            self.log.debug('client_id is %s' % client_id)
            redirect_uri = args['redirect_uri']
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

    def post(self):
        """
<<<<<<< HEAD
        Validates required login arguments sent from platform and then uses
        the ``authorize_redirect()`` to redirect users to the authorization url.
        """
        lti_utils = LTIUtils()
        validator = LTI13LaunchValidator()
        args = lti_utils.convert_request_to_dict(self.request.arguments)
        if validator.validate_authentication_request(args):
            login_hint = args['login_hint']
            self.log.debug('login_hint is %s' % login_hint)
            lti_message_hint = args['lti_message_hint']
            self.log.debug('lti_message_hint is %s' % lti_message_hint)
            client_id = args['client_id']
            self.log.debug('client_id is %s' % client_id)
            redirect_uri = args['redirect_uri']
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
=======
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
>>>>>>> 9cb6ef6... fix merge conflicts


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
