import os
import json

from jupyterhub.handlers import BaseHandler

from ltiauthenticator import LTIAuthenticator

from tornado.web import HTTPError
from tornado.httpclient import AsyncHTTPClient

from illumidesk.apis.jupyterhub_api import JupyterHubAPI
from illumidesk.handlers.lms_grades import LTIGradesSenderControlFile
from illumidesk.authenticators.utils import LTIUtils
from illumidesk.authenticators.validator import LTI11LaunchValidator


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
            # GRADES-SENDER >>>> retrieve assignment_name from standard property
            assignment_name = args['resource_link_title'] if 'resource_link_title' in args else 'unknown'
            if lms_vendor == 'canvas':
                self.log.debug('TC is a Canvas LMS instance')
                if 'custom_canvas_user_login_id' in args and args['custom_canvas_user_login_id'] is not None:
                    custom_canvas_user_id = args['custom_canvas_user_login_id']
                    username = lti_utils.email_to_username(custom_canvas_user_id)
                    self.log.debug('using custom_canvas_user_id for username')
                # GRADES-SENDER >>>> retrieve assignment_name from custom property
                assignment_name = (
                    args['custom_canvas_assignment_title'] if 'custom_canvas_assignment_title' in args else 'unknown'
                )
            else:
                if (
                    username == ''
                    and 'lis_person_contact_email_primary' in args
                    and args['lis_person_contact_email_primary'] is not None
                ):
                    email = args['lis_person_contact_email_primary']
                    username = lti_utils.email_to_username(email)
                    self.log.debug('using lis_person_contact_email_primary for username')
                elif 'lis_person_name_given' in args and args['lis_person_name_given'] is not None:
                    username = args['lis_person_name_given']
                    self.log.debug('using lis_person_name_given for username')
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

            # with all info extracted from lms request, register info for grades sender only if user is a STUDENT
            if user_role == 'Learner':
                control_file = LTIGradesSenderControlFile(f'/home/grader-{course_id}/{course_id}')
                # the next fields must come in args
                lis_outcome_service_url = args['lis_outcome_service_url']
                lis_result_sourcedid = args['lis_result_sourcedid']
                control_file.register_data(assignment_name, lis_outcome_service_url, lms_user_id, lis_result_sourcedid)

            return {
                'name': username,
                'auth_state': {
                    'course_id': course_id,
                    'lms_user_id': lms_user_id,
                    'user_role': user_role,
                },  # noqa: E231
            }

    async def post_auth_hook(self, authenticator, handler, authentication):
        """
        Calls the microservice to setup up a new course in case it does not exist.
        The data needed is received from auth_State within authentication object

        This function requires `Authenticator.enable_auth_state = True`.

        Args:
            authenticator: the JupyterHub Authenticator object
            handler: the JupyterHub handler object
            authentication: the authentication object returned by the
            authenticator class

        Returns:
            authentication (Required): updated authentication object
        """
        announcement_port = os.environ.get("ANNOUNCEMENT_SERVICE_PORT") or '8889'
        username = authentication['name']
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
        self.log.debug(f'Setup-Course service response: {resp_json}')

        # In case of new courses launched then execute a rolling update with jhub to reload our configuration file
        if 'is_new_setup' in resp_json and resp_json['is_new_setup'] is True:
            # notify the user the browser needs to be reload (when traefik redirects to a new jhub)
            url = f'http://localhost:{int(announcement_port)}/services/announcement'
            headers['Authorization'] = f'token {os.environ.get("JUPYTERHUB_API_TOKEN")}'
            body_data = {'announcement': 'A new service was detected, please reload this page...'}
            await client.fetch(url, headers=headers, body=json.dumps(body_data), method='POST')

            self.log.debug('The current jupyterhub instance will be updated by setup-course service...')
            url = f'http://{service_name}:{port}/rolling-update'
            # our setup-course not requires auth
            del headers['Authorization']
            # WE'RE NOT USING <<<AWAIT>>> because the rolling update should occur later
            client.fetch(url, headers=headers, body='', method='POST')

        return authentication


class LTI11AuthenticateHandler(BaseHandler):
    """
    LTI login handler obtained from jupyterhub/ltiauthenticator.

    If there's a custom parameter called 'next', will redirect user to
    that URL after authentication. Else, will send them to /home.
    """

    async def post(self):
        user = await self.login_user()  # noqa: F841
        self.redirect(self.get_body_argument('custom_next', self.get_next_url()))
