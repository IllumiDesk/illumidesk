import os
import json
import logging
import time

from pathlib import Path

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

from illumidesk.authenticators.grades import get_sender

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
        self.set_header('Content-Type', 'application/json')
        if not os.environ.get('PRIVATE_KEY'):
            raise ValueError('PRIVATE_KEY environment variable not set')
        private_key = os.environ.get('PRIVATE_KEY')
        kid = md5(private_key.encode('utf-8')).hexdigest()
        self.log.debug('kid is %s' % kid)
        public_key = RSA.importKey(private_key).publickey()
        self.log.debug('public_key is %s' % public_key)
        keys = {
            'keys': [
                {
                    'kty': 'RSA',
                    'alg': 'RS256',
                    'use': 'sig',
                    'kid': kid,
                    'n': long_to_base64(public_key.n),
                    'e': long_to_base64(public_key.e),
                }
            ]
        }
        self.write(json.dumps(keys))


class HelloWorldHandler(BaseHandler):
    def get(self):
        return 'Hello World!'


class FileSelectHandler(BaseHandler):
    """
    Handles file selection used to select files for assignments and
    modules from the LMS using LTI 1.3
    """

    async def get(self):
        """
        Gets the user's path for the course and then iterates through
        the list of folders/files so the user can select the file selector
        template.
        """
        user = self.current_user
        self.log.info('User %s initiating file selection' % user)
        decoded = self.authenticator.decoded
        path = Path(os.environ.get('NFS_ROOT'), self.authenticator.course_id)
        self.log.debug('Course directory for file select is %s' % path)
        files = []
        for f in self._iterate_dir(path):
            fpath = str(f.relative_to(path))
            self.log.debug('Getting files fpath %s' % fpath)
            url = f'https://{self.request.host}/hub/user/{user.name}/notebooks/{fpath}'
            self.log.debug('URL to fetch files is %s' % url)
            self.log.debug('Content items from fetched files are %s' % f.name)
            files.append(
                {
                    'path': fpath,
                    'content_items': json.dumps(
                        {
                            "@context": "http://purl.imsglobal.org/ctx/lti/v1/ContentItem",
                            "@graph": [
                                {
                                    "@type": "LtiLinkItem",
                                    "@id": url,
                                    "url": url,
                                    "title": f.name,
                                    "text": f.name,
                                    "mediaType": "application/vnd.ims.lti.v1.ltilink",
                                    "placementAdvice": {"presentationDocumentTarget": "frame"},
                                }
                            ],
                        }
                    ),
                }
            )
        self.log.debug('Rendering file-select.html template')
        html = self.render_template(
            'file-select.html',
            files=files,
            action_url=decoded['https://purl.imsglobal.org/spec/lti/claim/launch_presentation']['return_url'],
        )
        self.finish(html)

    def _iterate_dir(self, directory):
        """
        Uitility function to iterate through a directory to get a list of
        items from a directory.

        Yields:
          item: item from directory
        """
        for item in directory.iterdir():
            if item.name.startswith('.') or item.name.startswith('submissions'):
                continue
            if item.is_dir():
                yield from self._iterate_dir(item)
            else:
                self.log.debug('Found item %s' % item)
                yield item


class SendGradesHandler(BaseHandler):
    async def post(self, course_id, assignment):
        url = f'https://{self.request.host}'
        self.log.debug('Sending grades with url %s' % url)
        data = json.loads(self.request.body)
        sender = get_sender(course_id, assignment, data, url)
        self.log.debug('Sending grades with sender %s' % sender)
        await sender.send()
        self.finish(json.dumps({'message': 'OK'}))
