import os
import logging

from jupyterhub.auth import Authenticator
from jupyterhub.app import JupyterHub
from jupyterhub.handlers import BaseHandler

from ltiauthenticator import LTIAuthenticator

from oauthenticator.oauth2 import OAuthenticator

from tornado.web import HTTPError
from tornado.web import RequestHandler

from traitlets import Unicode

from typing import Dict

from illumidesk.apis.jupyterhub_api import JupyterHubAPI
from illumidesk.apis.announcement_service import AnnouncementService
from illumidesk.apis.nbgrader_service import NbGraderServiceHelper
from illumidesk.apis.setup_course_service import make_rolling_update
from illumidesk.apis.setup_course_service import register_new_service

from illumidesk.authenticators.handlers import LTI11AuthenticateHandler
from illumidesk.authenticators.handlers import LTI13LoginHandler
from illumidesk.authenticators.handlers import LTI13CallbackHandler
from illumidesk.authenticators.utils import LTIUtils, user_is_an_instructor
from illumidesk.authenticators.utils import user_is_a_student
from illumidesk.authenticators.validator import LTI11LaunchValidator
from illumidesk.authenticators.validator import LTI13LaunchValidator

from illumidesk.grades.senders import LTIGradesSenderControlFile


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def setup_course_hook(
    authenticator: Authenticator, handler: RequestHandler, authentication: Dict[str, str]
) -> Dict[str, str]:
    """
    Calls the microservice to setup up a new course in case it does not exist.
    The data needed is received from auth_state within authentication object. This
    function assumes that the required k/v's in the auth_state dictionary are available,
    since the Authenticator(s) validates the data beforehand.

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
    lti_utils = LTIUtils()
    jupyterhub_api = JupyterHubAPI()

    org = os.environ.get('ORGANIZATION_NAME')
    if not org:
        raise EnvironmentError('ORGANIZATION_NAME env-var is not set')
    # normalize the name and course_id strings in authentication dictionary
    course_id = lti_utils.normalize_string(authentication['auth_state']['course_id'])
    username = lti_utils.normalize_string(authentication['name'])
    lms_user_id = authentication['auth_state']['lms_user_id']
    user_role = authentication['auth_state']['user_role']
    # register the user (it doesn't matter if it is a student or instructor) with her/his lms_user_id in nbgrader
    await jupyterhub_api.add_user_to_nbgrader_gradebook(course_id, username, lms_user_id)
    # TODO: verify the logic to simplify groups creation and membership
    if user_is_a_student(user_role):
        # assign the user to 'nbgrader-<course_id>' group in jupyterhub and gradebook
        await jupyterhub_api.add_student_to_jupyterhub_group(course_id, username)
    elif user_is_an_instructor(user_role):
        # assign the user in 'formgrade-<course_id>' group
        await jupyterhub_api.add_instructor_to_jupyterhub_group(course_id, username)
    data = {
        'org': org,
        'course_id': course_id,
        'domain': handler.request.host,
    }
    setup_response = await register_new_service(data)

    # In case of new courses launched then execute a rolling update with jhub to reload our configuration file
    if 'is_new_setup' in setup_response and setup_response['is_new_setup'] is True:
        # notify the user the browser needs to be reload (when traefik redirects to a new jhub)
        await AnnouncementService.add_announcement('A new service was detected, please reload this page...')

        logger.debug('The current jupyterhub instance will be updated by setup-course service...')
        make_rolling_update()

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

    def get_handlers(self, app: JupyterHub) -> BaseHandler:
        return [('/lti/launch', LTI11AuthenticateHandler)]

    async def authenticate(self, handler: BaseHandler, data: Dict[str, str] = None) -> Dict[str, str]:  # noqa: C901
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

        self.log.debug('Original arguments received in request: %s' % handler.request.arguments)

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
            if 'tool_consumer_info_product_family_code' in args and args['tool_consumer_info_product_family_code']:
                lms_vendor = args['tool_consumer_info_product_family_code']

            # We use the course_id to setup the grader service notebook. Since this service
            # runs as a docker container we need to normalize the string so we can use it
            # as a container name.
            if 'context_label' in args and args['context_label']:
                course_id = args['context_label']
                self.log.debug('Course context_label normalized to: %s' % course_id)
            else:
                raise HTTPError(400, 'Course label not included in the LTI request')

            # Get the user's role, assign to Learner role by default. Roles are sent as institution
            # roles, where the roles' value is <handle>,<full URN>.
            # https://www.imsglobal.org/specs/ltiv1p0/implementation-guide#toc-16
            user_role = 'Learner'
            if 'roles' in args and args['roles']:
                user_role = args['roles'].split(',')[0]
                self.log.debug('User LTI role is: %s' % user_role)
            else:
                raise HTTPError(400, 'User role not included in the LTI request')

            # Assign the user_id. Check the tool consumer (lms) vendor. If canvas use their
            # custom user id extension by default, else use standar lti values.
            username = ''
            if lms_vendor == 'canvas':
                login_id = ''
                user_id = ''
                self.log.debug('TC is a Canvas LMS instance')
                if (
                    'custom_canvas_user_login_id' in args
                    and args['custom_canvas_user_login_id']
                    and 'custom_canvas_user_id' in args
                    and args['custom_canvas_user_id']
                ):
                    custom_canvas_user_login_id = args['custom_canvas_user_login_id']
                    login_id = lti_utils.email_to_username(custom_canvas_user_login_id)
                    self.log.debug('using custom_canvas_user_login_id for username')
                if 'custom_canvas_user_id' in args and args['custom_canvas_user_id']:
                    custom_canvas_user_id = args['custom_canvas_user_id']
                    user_id = lti_utils.email_to_username(custom_canvas_user_id)
                    self.log.debug('using custom_canvas_user_id for username')
                username = f'{login_id}-{user_id}'
            if (
                not username
                and 'lis_person_contact_email_primary' in args
                and args['lis_person_contact_email_primary']
            ):
                email = args['lis_person_contact_email_primary']
                username = lti_utils.email_to_username(email)
                self.log.debug('using lis_person_contact_email_primary for username')
            elif not username and 'lis_person_name_given' in args and args['lis_person_name_given']:
                username = args['lis_person_name_given']
                self.log.debug('using lis_person_name_given for username')
            elif not username and 'lis_person_sourcedid' in args and args['lis_person_sourcedid']:
                username = args['lis_person_sourcedid']
                self.log.debug('using lis_person_sourcedid for username')
            elif not username and 'lis_person_name_family' in args and args['lis_person_name_family']:
                username = args['lis_person_name_family']
                self.log.debug('using lis_person_name_family for username')
            elif not username and 'lis_person_name_full' in args and args['lis_person_name_full']:
                username = args['lis_person_name_full']
                self.log.debug('using lis_person_name_full for username')
            elif not username and 'user_id' in args and args['user_id']:
                username = args['user_id']
            elif not username:
                raise HTTPError(400, 'Unable to get username from request arguments')

            # use the user_id to identify the unique user id, if its not sent with the request
            # then default to the username
            lms_user_id = args['user_id'] if 'user_id' in args else username

            # GRADES-SENDER: fetch the information needed to register assignments within the control file
            # retrieve assignment_name from standard property vs custom lms properties
            assignment_name = ''
            # the next fields must come in args
            if 'custom_canvas_assignment_title' in args and args['custom_canvas_assignment_title']:
                assignment_name = lti_utils.normalize_string(args['custom_canvas_assignment_title'])
            # this requires adding a the assignment_title as a custom parameter in the tool consumer (lms)
            elif 'custom_assignment_title' in args and args['custom_assignment_title']:
                assignment_name = lti_utils.normalize_string(args['custom_assignment_title'])
            elif 'resource_link_title' in args and args['resource_link_title']:
                assignment_name = lti_utils.normalize_string(args['resource_link_title'])
            elif 'resource_link_id' in args and args['resource_link_id']:
                assignment_name = lti_utils.normalize_string(args['resource_link_id'])

            # Get lis_outcome_service_url and lis_result_sourcedid values that will help us to submit grades later
            lis_outcome_service_url = ''
            lis_result_sourcedid = ''

            # the next fields must come in args
            if 'lis_outcome_service_url' in args and args['lis_outcome_service_url']:
                lis_outcome_service_url = args['lis_outcome_service_url']
            if 'lis_result_sourcedid' in args and args['lis_result_sourcedid']:
                lis_result_sourcedid = args['lis_result_sourcedid']
            # only if both values exist we can register them to submit grades later
            if lis_outcome_service_url and lis_result_sourcedid:
                control_file = LTIGradesSenderControlFile(f'/home/grader-{course_id}/{course_id}')
                control_file.register_data(assignment_name, lis_outcome_service_url, lms_user_id, lis_result_sourcedid)
            # Assignment creation
            if assignment_name:
                nbgrader_service = NbGraderServiceHelper(course_id)
                self.log.debug(
                    'Creating a new assignment from the Authentication flow with title %s' % assignment_name
                )
                nbgrader_service.create_assignment_in_nbgrader(assignment_name)
            # ensure the user name is normalized
            username_normalized = lti_utils.normalize_string(username)
            self.log.debug('Assigned username is: %s' % username_normalized)

            return {
                'name': username_normalized,
                'auth_state': {
                    'course_id': course_id,
                    'lms_user_id': lms_user_id,
                    'user_role': user_role,
                },  # noqa: E231
            }


class LTI13Authenticator(OAuthenticator):
    """Custom authenticator used with LTI 1.3 requests"""

    login_service = 'LTI13Authenticator'

    # handlers used for login, callback, and jwks endpoints
    login_handler = LTI13LoginHandler
    callback_handler = LTI13CallbackHandler

    # the client_id, authorize_url, and token_url config settings
    # are available in the OAuthenticator base class. the are overrident here
    # for the sake of clarity.
    client_id = Unicode(
        '',
        help="""
        The LTI 1.3 client id that identifies the tool installation with the
        platform.
        """,
    ).tag(config=True)

    endpoint = Unicode(
        '',
        help="""
        The platform's base endpoint used when redirecting requests to the platform
        after receiving the initial login request.
        """,
    ).tag(config=True)

    oauth_callback_url = Unicode(
        os.getenv('LTI13_CALLBACK_URL', ''),
        config=True,
        help="""Callback URL to use.
        Should match the redirect_uri sent from the platform during the
        initial login request.""",
    ).tag(config=True)

    async def authenticate(  # noqa: C901
        self, handler: LTI13LoginHandler, data: Dict[str, str] = None
    ) -> Dict[str, str]:
        """
        Overrides authenticate from base class to handle LTI 1.3 authentication requests.

        Args:
          handler: handler object
          data: authentication dictionary

        Returns:
          Authentication dictionary
        """
        lti_utils = LTIUtils()
        validator = LTI13LaunchValidator()

        # get jwks endpoint and token to use as args to decode jwt. we could pass in
        # self.endpoint directly as arg to jwt_verify_and_decode() but logging the
        self.log.debug('JWKS platform endpoint is %s' % self.endpoint)
        id_token = handler.get_argument('id_token')
        self.log.debug('ID token issued by platform is %s' % id_token)

        # extract claims from jwt (id_token) sent by the platform. as tool use the jwks (public key)
        # to verify the jwt's signature.
        jwt_decoded = await validator.jwt_verify_and_decode(id_token, self.endpoint, False, audience=self.client_id)
        self.log.debug('Decoded JWT is %s' % jwt_decoded)

        if validator.validate_launch_request(jwt_decoded):
            course_id = jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/context']['label']
            self.log.debug('Normalized course label is %s' % course_id)
            username = ''
            if 'email' in jwt_decoded and jwt_decoded['email']:
                username = lti_utils.email_to_username(jwt_decoded['email'])
            elif 'name' in jwt_decoded and jwt_decoded['name']:
                username = jwt_decoded['name']
            elif 'given_name' in jwt_decoded and jwt_decoded['given_name']:
                username = jwt_decoded['given_name']
            elif 'family_name' in jwt_decoded and jwt_decoded['family_name']:
                username = jwt_decoded['family_name']
            elif (
                'https://purl.imsglobal.org/spec/lti/claim/lis' in jwt_decoded
                and 'person_sourcedid' in jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/lis']
                and jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/lis']['person_sourcedid']
            ):
                username = jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/lis']['person_sourcedid'].lower()
            elif (
                'lms_user_id' in jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/custom']
                and jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/custom']['lms_user_id']
            ):
                username = str(jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/custom']['lms_user_id'])
            self.log.debug('username is %s' % username)
            # ensure the username is normalized
            self.log.debug('username is %s' % username)
            if username == '':
                raise HTTPError('Unable to set the username')

            user_role = ''
            for role in jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/roles']:
                if role.find('Instructor') >= 1:
                    user_role = 'Instructor'
                elif role.find('Learner') >= 1 or role.find('Student') >= 1:
                    user_role = 'Learner'
            # set role to learner role if instructor or learner/student roles aren't
            # sent with the request
            if user_role == '':
                user_role = 'Learner'
            self.log.debug('user_role is %s' % user_role)

            lms_user_id = jwt_decoded['sub'] if 'sub' in jwt_decoded else username
            # Values for send-grades functionality
            resource_link = jwt_decoded['https://purl.imsglobal.org/spec/lti/claim/resource_link']
            resource_link_title = resource_link['title'] or ''
            course_lineitems = ''
            if (
                'https://purl.imsglobal.org/spec/lti-ags/claim/endpoint' in jwt_decoded
                and 'lineitems' in jwt_decoded['https://purl.imsglobal.org/spec/lti-ags/claim/endpoint']
            ):
                course_lineitems = jwt_decoded['https://purl.imsglobal.org/spec/lti-ags/claim/endpoint']['lineitems']
            nbgrader_service = NbGraderServiceHelper(course_id)
            nbgrader_service.update_course(lms_lineitems_endpoint=course_lineitems)
            if resource_link_title:
                # resource_link_title_normalize = lti_utils.normalize_string(resource_link_title)
                self.log.debug(
                    'Creating a new assignment from the Authentication flow with title %s' % resource_link_title
                )
                nbgrader_service.create_assignment_in_nbgrader(resource_link_title)

            # ensure the user name is normalized
            username_normalized = lti_utils.normalize_string(username)
            self.log.debug('Assigned username is: %s' % username_normalized)

            return {
                'name': username_normalized,
                'auth_state': {
                    'course_id': course_id,
                    'user_role': user_role,
                    'lms_user_id': lms_user_id,
                },  # noqa: E231
            }
