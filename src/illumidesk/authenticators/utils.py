import random
import re
import secrets
import time
import uuid

from jupyterhub.handlers import BaseHandler

from tornado.web import HTTPError
from tornado.web import RequestHandler

from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from traitlets.config import LoggingConfigurable


# Determined from https://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide
# This page also provides a nice summary of the required, recommended, and optional
# LTI 1.1 launch parameters: https://www.edu-apps.org/code.html. We define the user_id
# as required even though it is defined as recommended since we need this value to track
# this lms_user_id used in the grader db.
LTI11_LAUNCH_PARAMS_REQUIRED = [
    'lti_message_type',
    'lti_version',
    'resource_link_id',
    'user_id',
]

LTI11_LAUNCH_PARAMS_RECOMMENDED = [
    'resource_link_title',
    'roles',
    'lis_person_name_given',
    'lis_person_name_family',
    'lis_person_name_full',
    'lis_person_contact_email_primary',
    'context_id',
    'context_title',
    'context_label',
    'launch_presentation_locale',
    'launch_presentation_document_target',
    'launch_presentation_width',
    'launch_presentation_height',
    'launch_presentation_return_url',
    'tool_consumer_info_product_family_code',
    'tool_consumer_info_version',
    'tool_consumer_instance_guid',
    'tool_consumer_instance_name',
    'tool_consumer_instance_contact_email',
]

LTI11_LAUNCH_PARAMS_OTIONAL = [
    'resource_link_description',
    'user_image',
    'role_scope_mentor',
    'context_type',
    'launch_presentation_css_url',
    'tool_consumer_instance_description',
    'tool_consumer_instance_url',
]

LTI11_LIS_OPTION = [
    'lis_outcome_service_url',
    'lis_result_sourcedid',
    'lis_person_sourcedid',
    'lis_course_offering_sourcedid',
    'lis_course_section_sourcedid',
]

# https://www.imsglobal.org/specs/ltiv1p1/implementation-guide
# Section 4.2
LTI11_OAUTH_ARGS = [
    'oauth_consumer_key',
    'oauth_signature_method',
    'oauth_timestamp',
    'oauth_nonce',
    'oauth_callback',
    'oauth_version',
    'oauth_signature',
]

LAUNCH_PARAMS_REQUIRED = LTI11_LAUNCH_PARAMS_REQUIRED + LTI11_OAUTH_ARGS

LAUNCH_PARAMS_ALL = (
    LTI11_LAUNCH_PARAMS_REQUIRED
    + LTI11_LAUNCH_PARAMS_RECOMMENDED
    + LTI11_LAUNCH_PARAMS_OTIONAL
)


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
            hops = [
                h.strip()
                for h in handler.request.headers['x-forwarded-proto'].split(',')
            ]
            protocol = hops[0]
        else:
            protocol = handler.request.protocol

        return protocol

    def convert_request_to_dict(
        self, arguments: Dict[str, List[bytes]]
    ) -> Dict[str, str]:
        """
        Converts the arguments obtained from a request to a dict.

        Args:
          handler: a tornado.web.RequestHandler object

        Returns:
          A decoded dict with keys/values extracted from the request's arguments
        """
        args = {}
        for k, values in arguments.items():
            args[k] = (
                values[0].decode() if len(values) == 1 else [v.decode() for v in values]
            )
        return args
