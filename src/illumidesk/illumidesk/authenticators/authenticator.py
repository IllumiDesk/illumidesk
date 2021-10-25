import logging
import os
from typing import Any
from typing import Dict

from jupyterhub.auth import Authenticator
from oauthenticator.oauth2 import OAuthenticator
from tornado.web import HTTPError
from tornado.web import RequestHandler
from traitlets import Unicode

from illumidesk.apis.jupyterhub_api import JupyterHubAPI
from illumidesk.apis.nbgrader_service import NbGraderServiceHelper
from illumidesk.apis.setup_course_service import create_assignment_source_dir
from illumidesk.apis.setup_course_service import register_new_service
from illumidesk.authenticators.handlers import LTI13CallbackHandler
from illumidesk.authenticators.handlers import LTI13LoginHandler
from illumidesk.authenticators.utils import LTIUtils
from illumidesk.authenticators.utils import user_is_a_student
from illumidesk.authenticators.utils import user_is_an_instructor
from illumidesk.authenticators.validator import LTI13LaunchValidator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


ORG_NAME = os.environ.get("ORGANIZATION_NAME")
if not ORG_NAME:
    raise EnvironmentError("ORGANIZATION_NAME env-var is not set")


async def setup_course_hook_lti11(
    handler: RequestHandler,
    authentication: Dict[str, str],
) -> Dict[str, str]:
    """
    Calls the microservice to setup up a new course in case it does not exist when receiving
    LTI 1.1 launch requests. The data needed is received from auth_state within authentication object.
    This function assumes that the required k/v's in the auth_state dictionary are available,
    since the Authenticator(s) validates the data beforehand.

    This function requires `Authenticator.enable_auth_state = True` and is intended
    to be used as a post_auth_hook.

    Args:
        handler: the JupyterHub handler object
        authentication: the authentication object returned by the
            authenticator class

    Returns:
        authentication (Required): updated authentication object
    """
    lti_utils = LTIUtils()
    jupyterhub_api = JupyterHubAPI()

    # normalize the name and course_id strings in authentication dictionary
    username = authentication["name"]
    lms_user_id = authentication["auth_state"]["user_id"]
    user_role = authentication["auth_state"]["roles"].split(",")[0]
    course_id = lti_utils.normalize_string(
        authentication["auth_state"]["context_label"]
    )
    nb_service = NbGraderServiceHelper(course_id, True)

    # register the user (it doesn't matter if it is a student or instructor) with her/his lms_user_id in nbgrader
    nb_service.add_user_to_nbgrader_gradebook(username, lms_user_id)
    # TODO: verify the logic to simplify groups creation and membership
    if user_is_a_student(user_role):
        try:
            # assign the user to 'nbgrader-<course_id>' group in jupyterhub and gradebook
            await jupyterhub_api.add_student_to_jupyterhub_group(course_id, username)
        except Exception as e:
            logger.error(
                "An error when adding student username: %s to course_id: %s with exception %s",
                (username, course_id, e),
            )
    elif user_is_an_instructor(user_role):
        try:
            # assign the user in 'formgrade-<course_id>' group
            await jupyterhub_api.add_instructor_to_jupyterhub_group(course_id, username)
        except Exception as e:
            logger.error(
                "An error when adding instructor username: %s to course_id: %s with exception %s",
                (username, course_id, e),
            )

    # launch the new grader-notebook as a service
    try:
        _ = await register_new_service(org_name=ORG_NAME, course_id=course_id)
    except Exception as e:
        logger.error("Unable to launch the shared grader notebook with exception %s", e)

    return authentication


async def setup_course_hook(
    authenticator: Authenticator,
    handler: RequestHandler,
    authentication: Dict[str, str],
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

    # normalize the name and course_id strings in authentication dictionary
    course_id = lti_utils.normalize_string(authentication["auth_state"]["course_id"])
    nb_service = NbGraderServiceHelper(course_id, True)
    username = lti_utils.normalize_string(authentication["name"])
    lms_user_id = authentication["auth_state"]["lms_user_id"]
    user_role = authentication["auth_state"]["user_role"]

    # register the user (it doesn't matter if it is a student or instructor) with her/his lms_user_id in nbgrader
    nb_service.add_user_to_nbgrader_gradebook(username, lms_user_id)
    # TODO: verify the logic to simplify groups creation and membership
    if user_is_a_student(user_role):
        try:
            # assign the user to 'nbgrader-<course_id>' group in jupyterhub and gradebook
            await jupyterhub_api.add_student_to_jupyterhub_group(course_id, username)
        except Exception as e:
            logger.error(
                "An error when adding student username: %s to course_id: %s with exception %s",
                (username, course_id, e),
            )
    elif user_is_an_instructor(user_role):
        try:
            # assign the user in 'formgrade-<course_id>' group
            await jupyterhub_api.add_instructor_to_jupyterhub_group(course_id, username)
        except Exception as e:
            logger.error(
                "An error when adding instructor username: %s to course_id: %s with exception %s",
                (username, course_id, e),
            )

    # launch the new grader-notebook as a service
    try:
        _ = await register_new_service(org_name=ORG_NAME, course_id=course_id)
    except Exception as e:
        logger.error("Unable to launch the shared grader notebook with exception %s", e)

    return authentication


class LTI13Authenticator(OAuthenticator):
    """Custom authenticator used with LTI 1.3 requests"""

    login_service = "LTI13Authenticator"

    # handlers used for login, callback, and jwks endpoints
    login_handler = LTI13LoginHandler
    callback_handler = LTI13CallbackHandler

    # the client_id, authorize_url, and token_url config settings
    # are available in the OAuthenticator base class. the are overrident here
    # for the sake of clarity.
    client_id = Unicode(
        "",
        help="""
        The LTI 1.3 client id that identifies the tool installation with the
        platform.
        """,
    ).tag(config=True)

    endpoint = Unicode(
        "",
        help="""
        The platform's base endpoint used when redirecting requests to the platform
        after receiving the initial login request.
        """,
    ).tag(config=True)

    oauth_callback_url = Unicode(
        os.getenv("LTI13_CALLBACK_URL", ""),
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
        self.log.debug("JWKS platform endpoint is %s" % self.endpoint)
        id_token = handler.get_argument("id_token")
        self.log.debug("ID token issued by platform is %s" % id_token)

        # extract claims from jwt (id_token) sent by the platform. as tool use the jwks (public key)
        # to verify the jwt's signature.
        jwt_decoded = await validator.jwt_verify_and_decode(
            id_token, self.endpoint, False, audience=self.client_id
        )
        self.log.debug("Decoded JWT is %s" % jwt_decoded)

        if validator.validate_launch_request(jwt_decoded):
            course_id = jwt_decoded[
                "https://purl.imsglobal.org/spec/lti/claim/context"
            ]["label"]
            course_id = lti_utils.normalize_string(course_id)
            self.log.debug("Normalized course label is %s" % course_id)
            username = ""
            if "email" in jwt_decoded and jwt_decoded["email"]:
                username = lti_utils.email_to_username(jwt_decoded["email"])
            elif "name" in jwt_decoded and jwt_decoded["name"]:
                username = jwt_decoded["name"]
            elif "given_name" in jwt_decoded and jwt_decoded["given_name"]:
                username = jwt_decoded["given_name"]
            elif "family_name" in jwt_decoded and jwt_decoded["family_name"]:
                username = jwt_decoded["family_name"]
            elif (
                "https://purl.imsglobal.org/spec/lti/claim/lis" in jwt_decoded
                and "person_sourcedid"
                in jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/lis"]
                and jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/lis"][
                    "person_sourcedid"
                ]
            ):
                username = jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/lis"][
                    "person_sourcedid"
                ].lower()
            elif (
                "lms_user_id"
                in jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/custom"]
                and jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/custom"][
                    "lms_user_id"
                ]
            ):
                username = str(
                    jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/custom"][
                        "lms_user_id"
                    ]
                )

            # set role to learner role (by default) if instructor or learner/student roles aren't
            # sent with the request
            user_role = "Learner"
            for role in jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/roles"]:
                if role.find("Instructor") >= 1:
                    user_role = "Instructor"
                elif role.find("Learner") >= 1 or role.find("Student") >= 1:
                    user_role = "Learner"
            self.log.debug("user_role is %s" % user_role)

            launch_return_url = ""
            if (
                "https://purl.imsglobal.org/spec/lti/claim/launch_presentation"
                in jwt_decoded
                and "return_url"
                in jwt_decoded[
                    "https://purl.imsglobal.org/spec/lti/claim/launch_presentation"
                ]
            ):
                launch_return_url = jwt_decoded[
                    "https://purl.imsglobal.org/spec/lti/claim/launch_presentation"
                ]["return_url"]
            # if there is a resource link request then process additional steps
            if not validator.is_deep_link_launch(jwt_decoded):
                await process_resource_link_lti_13(self.log, course_id, jwt_decoded)

            lms_user_id = jwt_decoded["sub"] if "sub" in jwt_decoded else username

            # ensure the username is normalized
            self.log.debug("username is %s" % username)
            if not username:
                raise HTTPError(400, "Unable to set the username")

            # ensure the user name is normalized
            username_normalized = lti_utils.normalize_string(username)
            self.log.debug("Assigned username is: %s" % username_normalized)

            return {
                "name": username_normalized,
                "auth_state": {
                    "course_id": course_id,
                    "user_role": user_role,
                    "lms_user_id": lms_user_id,
                    "launch_return_url": launch_return_url,
                },  # noqa: E231
            }


async def process_resource_link_lti_13(
    logger: Any,
    course_id: str,
    jwt_body_decoded: Dict[str, Any],
) -> None:
    """
    Executes additional processes with the claims that come only with LtiResourceLinkRequest
    """
    # Values for send-grades functionality
    resource_link = jwt_body_decoded[
        "https://purl.imsglobal.org/spec/lti/claim/resource_link"
    ]
    resource_link_title = resource_link["title"] or ""
    nbgrader_service = NbGraderServiceHelper(course_id, True)
    if resource_link_title:
        assignment_name = LTIUtils().normalize_string(resource_link_title)
        logger.debug(
            "Creating a new assignment from the Authentication flow with title %s"
            % assignment_name
        )
        # register the new assignment in nbgrader database
        nbgrader_service.register_assignment(assignment_name)
        # create the assignment source directory by calling the grader-setup service
        await create_assignment_source_dir(ORG_NAME, course_id, assignment_name)
