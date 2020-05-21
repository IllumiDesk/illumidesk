import logging
import json
import re
import time
import urllib
import uuid

import jwt

from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClientError
from tornado.web import RequestHandler

from typing import Dict
from typing import List

from traitlets.config import LoggingConfigurable


class LTIUtils(LoggingConfigurable):
    """
    A class which contains various utility functions
    which work in conjunction with LTI requests.
    """

    def normalize_name_for_containers(self, name: str) -> str:
        """
        Function used to strip special characters and convert strings
        to docker container compatible names. This function is used mostly
        with course labels, as they are used for the shared grader notebook
        container names.

        Args:
          name: The string to normalize for docker container and volume
            names (e.g. Dev-IllumiDesk)

        Returns:
          normalized_name: The normalized string
        """
        if not name:
            raise ValueError('Name is empty')
        # truncate name after 30th character
        name = (name[:30] + '') if len(name) > 30 else name
        # remove special characters
        name = re.sub(r'[^\w-]+', '', name)
        # if the first character is any of _.- remove it
        name = name.lstrip('_.-')
        # convert to lower case
        name = name.lower()
        # limit course_id to 22 characters, since its used for o/s username
        # in jupyter/docker-stacks compatible grader notebook (NB_USER)
        normalized_name = name[0:20]
        self.log.debug('String normalized to %s' % normalized_name)
        return normalized_name

    def email_to_username(self, email: str) -> str:
        """
        Normalizes an email to get a username. This function
        calculates the username by getting the string before the
        @ symbol, removing special characters, removing comments,
        converting string to lowercase, and adds 1 if the username
        has an integer value already in the string.

        Args:
          email: A valid email address
        
        Returns:
          username: A username string

        Raises:
          ValueError if email is empty
        """
        if not email:
            raise ValueError('email is missing')
        username = email.split('@')[0]
        username = username.split('+')[0]
        username = re.sub(r'\([^)]*\)', '', username)
        username = re.sub(r'[^\w-]+', '', username)
        username = username.lower()
        self.log.debug('Username normalized to %s' % username)
        return username

    def get_client_protocol(self, handler: RequestHandler) -> Dict[str, str]:
        """
        This is a copy of the jupyterhub-ltiauthenticator logic to get the first
        protocol value from the x-forwarded-proto list, assuming there is more than
        one value. Otherwise, this returns the value as-is.

        Extracted as a method to facilitate testing.

        Args:
          handler: a tornado.web.RequestHandler object

        Returns:
          A decoded dict with keys/values extracted from the request's arguments
        """
        if 'x-forwarded-proto' in handler.request.headers:
            hops = [h.strip() for h in handler.request.headers['x-forwarded-proto'].split(',')]
            protocol = hops[0]
        else:
            protocol = handler.request.protocol

        return protocol

    def convert_request_to_dict(self, arguments: Dict[str, List[bytes]]) -> Dict[str, str]:
        """
        Converts the arguments obtained from a request to a dict.

        Args:
          handler: a tornado.web.RequestHandler object

        Returns:
          A decoded dict with keys/values extracted from the request's arguments
        """
        args = {}
        for k, values in arguments.items():
            args[k] = values[0].decode() if len(values) == 1 else [v.decode() for v in values]
        return args

    async def get_lms_access_token(
        self, iss: str, token_url: str, private_key: str, client_id: str, scope=None
    ) -> Dict[str, str]:
        """
        Gets the LTI 1.3 compatible LMS access token used to authenticate requests from
        the tool with the platform. Example use-cases include sending grades, fetching users
        by group membership, among others.

        Args:
          iss: launch request Issuer. If the request originates from a Canvas cloud version
            then this value will mostly likely be https://canvas.instructure.com.
          token_url: token endpoint for the LMS such as https://my.lms.domain/login/oauth2/token
          private_key: private key used to sign token request
          client_id: client id for installed external tool
          scope: scope desired when requesting token, such as lineitem, score, and results

        Returns:
          Valid token in json format
        """
        if not iss:
            raise ValueError('missing issuer')
        if not token_url:
            raise ValueError('missing token url')
        if not private_key:
            raise ValueError('missing private_key')
        if not client_id:
            raise ValueError('missing client_id')
        token_params = {
            'iss': iss,
            'sub': client_id,
            'aud': token_url,
            'exp': int(time.time()) + 600,
            'iat': int(time.time()),
            'jti': uuid.uuid4().hex,
        }
        self.logger.debug('Getting lms access token with parameters %s' % token_params)
        token = jwt.encode(token_params, private_key, algorithm='RS256',)
        self.logger.debug('Obtaining token %s' % token)
        scope = scope or ' '.join(
            [
                'https://purl.imsglobal.org/spec/lti-ags/scope/score',
                'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem',
                'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly',
            ]
        )
        self.logger.debug('Scope is %s' % scope)
        params = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': token.decode(),
            'scope': scope,
        }
        self.logger.debug('OAuth parameters are %s' % params)
        client = AsyncHTTPClient()
        body = urllib.parse.urlencode(params)
        try:
            resp = await client.fetch(token_url, method='POST', body=body, headers=None)
        except HTTPClientError as e:
            logging.info('Error fecthing lms access token %s' % e.response.body)
            raise
        self.logger.debug('Token response body is %s' % json.loads(resp.body))
        return json.loads(resp.body)
