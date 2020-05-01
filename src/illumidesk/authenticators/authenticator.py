import os
import json
import jwt
import logging

from josepy.jws import JWS
from josepy.jws import Header

from ltiauthenticator import LTIAuthenticator

from oauthenticator.oauth2 import OAuthenticator

from tornado import web
from tornado.httpclient import AsyncHTTPClient
from tornado.web import HTTPError

from traitlets import Unicode

from illumidesk.apis.jupyterhub_api import JupyterHubAPI
from illumidesk.authenticators.handlers import LTI11AuthenticateHandler
from illumidesk.authenticators.handlers import LTI13LoginHandler
from illumidesk.authenticators.handlers import LTI13CallbackHandler
from illumidesk.authenticators.utils import LTIUtils
from illumidesk.authenticators.validator import LTI11LaunchValidator


logger = logging.getLogger(__name__)


async def setup_course_hook(authenticator, handler, authentication):
    """
    Calls the microservice to setup up a new course in case it does not exist.
    The data needed is received from auth_State within authentication object

    This function requires `Authenticator.enable_auth_state = True` and is intended
    to be used as a post_auth_hook.

    Args:
        authenticator: the JupyterHub Authenticator object
        handler: the JupyterHub handler object
        authentication: the authentication object returned by the
        authenticator class

    Returns:
        authentication (Required): updated authentication object
    """
    announcement_port = os.environ.get('ANNOUNCEMENT_SERVICE_PORT') or '8889'
    username = authentication['name']
    if 'lms_user_id' in authentication['auth_state']:
        lms_user_id = authentication['auth_state']['lms_user_id']

    course_id = authentication['auth_state']['course_id']
    role = authentication['auth_state']['user_role']
    org = os.environ.get('ORGANIZATION_NAME')
    jupyterhub_api = JupyterHubAPI()
    # TODO: verify the logic to simplify groups creation and membership
    if role == 'Student' or role == 'Learner':
        # assign the user to 'nbgrader-<course_id>' group in jupyterhub and gradebook
        await jupyterhub_api.add_student_to_jupyterhub_group(course_id, username)
        await jupyterhub_api.add_user_to_nbgrader_gradebook(course_id, username, lms_user_id)
    elif role == 'Instructor':
        # assign the user in 'formgrade-<course_id>' group
        await jupyterhub_api.add_instructor_to_jupyterhub_group(course_id, username)
    client = AsyncHTTPClient()
    data = {
        'org': org,
        'course_id': course_id,
        'domain': handler.request.host,
    }
    service_name = os.environ.get('DOCKER_SETUP_COURSE_SERVICE_NAME') or 'setup-course'
    port = os.environ.get('DOCKER_SETUP_COURSE_PORT') or '8000'
    url = f'http://{service_name}:{port}'
    headers = {'Content-Type': 'application/json'}
    response = await client.fetch(url, headers=headers, body=json.dumps(data), method='POST')
    resp_json = json.loads(response.body)
    logger.debug(f'Setup-Course service response: {resp_json}')

    # In case of new courses launched then execute a rolling update with jhub to reload our configuration file
    if 'is_new_setup' in resp_json and resp_json['is_new_setup'] is True:
        # notify the user the browser needs to be reload (when traefik redirects to a new jhub)
        url = f'http://localhost:{int(announcement_port)}/services/announcement'
        jupyterhub_api_token = os.environ.get('JUPYTERHUB_API_TOKEN')
        headers['Authorization'] = f'token {jupyterhub_api_token}'
        body_data = {'announcement': 'A new service was detected, please reload this page...'}
        await client.fetch(url, headers=headers, body=json.dumps(body_data), method='POST')

        logger.debug('The current jupyterhub instance will be updated by setup-course service...')
        url = f'http://{service_name}:{port}/rolling-update'
        # our setup-course not requires auth
        del headers['Authorization']
        # WE'RE NOT USING <<<AWAIT>>> because the rolling update should occur later
        client.fetch(url, headers=headers, body='', method='POST')

    return authentication


class LTI11Authenticator(LTIAuthenticator):
    """
    JupyterHub LTI 1.1 Authenticator which extends the ltiauthenticator.LTIAuthenticator class.
    Messages sent to this authenticator are sent from a tool consumer (TC), such as
    an LMS. JupyterHub, as the authenticator, works as the tool provider (TP), also
    known as the external tool.

    The LTIAuthenticator base class defines the consumers, defined as 1 or (n) consumer key
    and shared secret k/v's to verify requests from their tool consumer.
    """

    def get_handlers(self, app):
        return [('/lti/launch', LTI11AuthenticateHandler)]

    async def authenticate(self, handler, data=None):
        """
        LTI 1.1 authenticator which overrides authenticate function from base LTIAuthenticator.
        After validating the LTI 1.1 signuature, this function decodes the dictionary object
        from the request payload to set normalized strings for the course_id, username,
        user role, and lms user id. Once those values are set they are added to the auth_state
        and returned as a dictionary for further processing by hooks defined in jupyterhub_config.

        One or more consumer keys/values must be set in the jupyterhub config with the
        LTIAuthenticator.consumers dict.

        Args:
            handler: JupyterHub's Authenticator handler object. For LTI 1.1 requests, the handler is
              an instance of LTIAuthenticateHandler.
            data: optional data object

        Returns:
            Authentication's auth_state dictionary

        Raises:
            HTTPError if the required values are not in the request
        """
        validator = LTI11LaunchValidator(self.consumers)
        lti_utils = LTIUtils()

        # extract the request arguments to a dict
        args = lti_utils.convert_request_to_dict(handler.request.arguments)
        self.log.debug('Decoded args from request: %s' % args)

        # get the origin protocol
        protocol = lti_utils.get_client_protocol(handler)
        self.log.debug('Origin protocol is: %s' % protocol)

        # build the full launch url value required for oauth1 signatures
        launch_url = f'{protocol}://{handler.request.host}{handler.request.uri}'
        self.log.debug('Launch url is: %s' % launch_url)

        if validator.validate_launch_request(launch_url, handler.request.headers, args):
            # get the lms vendor to implement optional logic for said vendor
            lms_vendor = ''
            if (
                'tool_consumer_info_product_family_code' in args
                and args['tool_consumer_info_product_family_code'] is not None
            ):
                lms_vendor = args['tool_consumer_info_product_family_code']

            # We use the course_id to setup the grader service notebook. Since this service
            # runs as a docker container we need to normalize the string so we can use it
            # as a container name.
            if 'context_label' in args and args['context_label'] is not None:
                course_label = args['context_label']
                course_id = lti_utils.normalize_name_for_containers(course_label)
                self.log.debug('Course context_label normalized to: %s' % course_id)
            else:
                raise HTTPError(400, 'Course label not included in the LTI request')

            # Get the user's role, assign to Learner role by default. Roles are sent as institution
            # roles, where the roles' value is <handle>,<full URN>.
            # https://www.imsglobal.org/specs/ltiv1p0/implementation-guide#toc-16
            user_role = 'Learner'
            if 'roles' in args and args['roles'] is not None:
                user_role = args['roles'].split(',')[0]
                self.log.debug('User LTI role is: %s' % user_role)
            else:
                raise HTTPError(400, 'User role not included in the LTI request')

            # Assign the user_id. Check the tool consumer (lms) vendor. If canvas use their
            # custom user id extension by default, else use standar lti values.
            username = ''
            if lms_vendor == 'canvas':
                self.log.debug('TC is a Canvas LMS instance')
                if 'custom_canvas_user_login_id' in args and args['custom_canvas_user_login_id'] is not None:
                    custom_canvas_user_id = args['custom_canvas_user_login_id']
                    username = lti_utils.email_to_username(custom_canvas_user_id)
                    self.log.debug('using custom_canvas_user_id for username')
                elif (
                    'lis_person_contact_email_primary' in args and args['lis_person_contact_email_primary'] is not None
                ):
                    email = args['lis_person_contact_email_primary']
                    username = lti_utils.email_to_username(email)
                    self.log.debug('using lis_person_contact_email_primary for username')
                elif 'lis_person_sourcedid' in args and args['lis_person_sourcedid'] is not None:
                    username = args['lis_person_sourcedid']
                    self.log.debug('using lis_person_sourcedid for username')
            else:
                if 'lis_person_contact_email_primary' in args and args['lis_person_contact_email_primary'] is not None:
                    email = args['lis_person_contact_email_primary']
                    username = lti_utils.email_to_username(email)
                    self.log.debug('using lis_person_contact_email_primary for username')
                elif 'lis_person_sourcedid' in args and args['lis_person_sourcedid'] is not None:
                    username = args['lis_person_sourcedid']
                    self.log.debug('using lis_person_sourcedid for username')
            if username == '':
                self.log.debug('using user_id for username')
                if 'user_id' in args and args['user_id'] is not None:
                    username = args['user_id']
                else:
                    raise HTTPError(400, 'Unable to get username from request arguments')
            self.log.debug('Assigned username is: %s' % username)

            # use the user_id as the lms_user_id, used to map usernames to lms user ids
            lms_user_id = args['user_id']

            return {
                'name': username,
                'auth_state': {
                    'course_id': course_id,
                    'lms_user_id': lms_user_id,
                    'user_role': user_role,
                },  # noqa: E231
            }


class LTI13Authenticator(OAuthenticator):
    login_service = 'LTI13Authenticator'
    # custom config
    endpoint = Unicode(config=True)
    # configs defined in OAuthenticator
    authorize_url = Unicode(config=True)
    token_url = Unicode(config=True)
    # handlers used for login, callback, and jwks endpoints
    login_handler = LTI13LoginHandler
    callback_handler = LTI13CallbackHandler

    async def retrieve_matching_jwk(self, token, endpoint, verify):
        client = AsyncHTTPClient()
        resp = await client.fetch(endpoint, validate_cert=verify)
        self.log.debug('Retrieving matching jwk %s' % json.loads(resp.body))
        return json.loads(resp.body)

    async def jwt_decode(self, token, jwks, verify=True, audience=None):
        if verify is False:
            self.log.debug('JWK verification is off, returning token %s' % jwt.decode(token, verify=False))
            return jwt.decode(token, verify=False)
        jwks = await self.retrieve_matching_jwk(token, jwks, verify)
        jws = JWS.from_compact(bytes(token, 'utf-8'))
        self.log.debug('Retrieving matching jws %s' % jws)
        json_header = jws.signature.protected
        header = Header.json_loads(json_header)
        self.log.debug('Header from decoded jwt %s' % header)
        key = None
        for jwk in jwks['keys']:
            if jwk['kid'] != header.kid:
                continue
            key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
            self.log.debug('Get keys from jwks dict  %s' % key)
        if key is None:
            self.log.debug('Key is None, returning None')
            return None
        self.log.debug('Returning decoded jwt with token %s key %s and verify %s' % (token, key, verify))
        return jwt.decode(token, key, verify, audience=audience)

    async def authenticate(self, handler, data=None):
        lti_utils = LTIUtils()

        # extract the request arguments to a dict
        args = lti_utils.convert_request_to_dict(handler.request.arguments)
        self.log.debug('Decoded args from request: %s' % args)

        # get the origin protocol
        protocol = lti_utils.get_client_protocol(handler)
        self.log.debug('Origin protocol is: %s' % protocol)

        # build the url used for
        url = f'{protocol}://{handler.request.host}'

        self.log.debug('Request host URL %s' % url)
        jwks = f'{self.endpoint}/api/lti/security/jwks'
        self.log.debug('JWKS endpoint is %s' % jwks)
        id_token = handler.get_argument('id_token')
        self.log.debug('ID token is %s' % id_token)
        decoded = await self.jwt_decode(id_token, jwks, audience=self.client_id)
        self.log.debug('Decoded JWT is %s' % decoded)
        self.decoded = decoded
        if self.decoded is None:
            raise web.HTTPError(403)
        self.course_id = decoded['https://purl.imsglobal.org/spec/lti/claim/context']['label']
        self.log.debug('course_label is %s' % self.course_id)
        # TODO: add conditional in case the tool installation has setting set to private mode
        username = lti_utils.email_to_username(decoded['email'])
        self.log.debug('username is %s' % self.username)
        lms_course_id = decoded['https://purl.imsglobal.org/spec/lti-ags/claim/endpoint']['lineitems'].split('/')[-2]
        self.log.debug('lms_course_id is %s' % self.username)
        org = handler.request.host.split('.')[0]
        self.log.debug('org is %s' % org)
        user_role = 'Instructor'
        if (
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner'
            in decoded['https://purl.imsglobal.org/spec/lti/claim/roles']
        ):
            user_role = 'Learner'
        self.log.debug('user_role is %s' % user_role)
        return {
            'name': username,
            'auth_state': {
                'course_id': self.course_id,
                'user_role': user_role,
                'lms_instance': self.endpoint,
                'token': await lti_utils.get_lms_access_token(
                    url, self.token_url, os.environ['PRIVATE_KEY'], decoded['aud'],
                ),
            },
        }
