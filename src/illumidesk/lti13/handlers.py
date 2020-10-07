import os
import json
from pathlib import Path

import pem

from Crypto.PublicKey import RSA

from jupyterhub.handlers import BaseHandler

from illumidesk.authenticators.utils import LTIUtils
from illumidesk.lti13.auth import get_jwk

from tornado import web

from urllib.parse import urlencode
from urllib.parse import quote


class LTI13ConfigHandler(BaseHandler):
    """
    Handles JSON configuration file for LTI 1.3
    """

    async def get(self) -> None:
        """
        Gets the JSON config which is used by LTI platforms
        to install the external tool.

        - The extensions key contains settings for specific vendors, such as canvas,
        moodle, edx, among others.
        - The tool uses public settings by default. Users that wish to install the tool with
        private settings should either copy/paste the json or toggle the application to private
        after it is installed with the platform.
        - Usernames are obtained by first attempting to get and normalize values sent when
        tools are installed with public settings. If private, the username is set using the
        anonumized user data when requests are sent with private installation settings.
        """
        lti_utils = LTIUtils()
        self.set_header('Content-Type', 'application/json')

        # get the origin protocol
        protocol = lti_utils.get_client_protocol(self)
        self.log.debug('Origin protocol is: %s' % protocol)
        # build the full target link url value required for the jwks endpoint
        target_link_url = f'{protocol}://{self.request.host}/'
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
                                'custom_fields': {
                                    'email': '$Person.email.primary',
                                    'lms_user_id': '$User.id',
                                },  # noqa: E231
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
            'description': 'IllumiDesk Learning Tools Interoperability (LTI) v1.3 tool.',
            'custom_fields': {
                'email': '$Person.email.primary',
                'lms_user_id': '$User.id',
            },  # noqa: E231
            'public_jwk_url': f'{target_link_url}hub/lti13/jwks',
            'target_link_uri': target_link_url,
            'oidc_initiation_url': f'{target_link_url}hub/oauth_login',
        }
        self.write(json.dumps(keys))


class LTI13JWKSHandler(BaseHandler):
    """
    Handler to serve our JWKS
    """

    def get(self) -> None:
        """
        - This method requires that the LTI13_PRIVATE_KEY environment variable
        is set with the full path to the RSA private key in PEM format.
        """
        if not os.environ.get('LTI13_PRIVATE_KEY'):
            raise EnvironmentError('LTI13_PRIVATE_KEY environment variable not set')
        key_path = os.environ.get('LTI13_PRIVATE_KEY')
        # check the pem permission
        if not os.access(key_path, os.R_OK):
            self.log.error(f'The pem file {key_path} cannot be load')
            raise PermissionError()
        private_key = pem.parse_file(key_path)
        public_key = RSA.import_key(private_key[0].as_text()).publickey().exportKey()
        self.log.debug('public_key is %s' % public_key)

        jwk = get_jwk(public_key)
        self.log.debug('the jwks is %s' % jwk)
        keys_obj = {'keys': []}
        keys_obj['keys'].append(jwk)
        # we do not need to use json.dumps because tornado is converting our dict automatically and adding the content-type as json
        # https://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.write
        self.write(keys_obj)


class FileSelectHandler(BaseHandler):
    @web.authenticated
    async def get(self):
        """Return a sorted list of notebooks recursively found in shared path"""
        user = self.current_user
        auth_state = await user.get_auth_state()
        self.log.debug('Current user for file select handler is %s' % user.name)
        # decoded = self.authenticator.decoded
        self.course_id = auth_state['course_id']
        self.grader_name = f'grader-{self.course_id}'
        self.grader_root = Path(
            '/home',
            self.grader_name,
        )
        self.course_root = self.grader_root / self.course_id
        self.course_shared_folder = Path('/shared', self.course_id)
        a = ''
        link_item_files = []
        notebooks = list(self.course_shared_folder.glob('**/*.ipynb'))
        notebooks.sort()
        for f in notebooks:
            fpath = str(f.relative_to(self.course_shared_folder))
            self.log.debug('Getting files fpath %s' % fpath)

            if fpath.startswith('.') or f.name.startswith('.'):
                self.log.debug('Ignoring file %s' % fpath)
                continue
            # generate the assignment link that uses gitpuller
            user_redirect_path = quote('/user-redirect/git-pull', safe='')
            assignment_link_path = f'?next={user_redirect_path}'
            urlpath_workspace = f'tree/{self.course_id}/{fpath}'
            self.log.debug(f'urlpath_workspace:{urlpath_workspace}')
            query_params_for_git = [
                ('repo', f'/home/jovyan/shared/{self.course_id}'),
                ('branch', 'master'),
                ('urlpath', urlpath_workspace),
            ]
            encoded_query_params_without_safe_chars = quote(urlencode(query_params_for_git), safe='')

            url = f'https://{self.request.host}/{assignment_link_path}?{encoded_query_params_without_safe_chars}'
            self.log.debug('URL to fetch files is %s' % url)
            link_item_files.append(
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
            'file_select.html',
            files=link_item_files,
            action_url=auth_state['launch_return_url'],
        )
        self.finish(html)
