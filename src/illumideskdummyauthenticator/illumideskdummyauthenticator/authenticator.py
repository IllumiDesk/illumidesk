from typing import Any
from typing import Dict

from jupyterhub.app import JupyterHub
from jupyterhub.auth import Authenticator
from jupyterhub.handlers import BaseHandler

from .handlers import IllumiDeskDummyLoginHandler
from .validators import IllumiDeskDummyValidator


class IllumiDeskDummyAuthenticator(Authenticator):
    """
    JupyterHub Authenticator that fetches a course name, assignment name, lms user id, and user role from standard form
    data.

    Args:
      handler: JupyterHub's Authenticator handler object. For test (aka Dummy) requests, the handler is
        an instance of IllumiDeskDummyAuthenticatorHandler.
      data: optional data object

    Returns:
      Authentication's auth_state dictionary

    Raises:
      HTTPError if the required values are not in the request
    """

    def get_handlers(self, app: JupyterHub) -> BaseHandler:
        return [("/dummy/login", IllumiDeskDummyLoginHandler)]

    async def authenticate(  # noqa: C901
        self, handler: BaseHandler, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:  # noqa: C901
        """Allow any user/pass combo"""

        validator = IllumiDeskDummyValidator()

        # extract the request arguments to a dict
        args = {}
        for k, values in handler.request.arguments.items():
            args[k] = values[0].decode()
        self.log.debug("Decoded args from request: %s" % args)

        if validator.validate_login_request(args):
            # get the lms vendor to implement optional logic for said vendor
            username = args["username"]
            assignment_name = args["assignment_name"]
            course_id = args["course_id"]
            lms_user_id = args["lms_user_id"]
            user_role = args["user_role"]

            auth_dict = {
                "name": username,
                "auth_state": {
                    "assignment_name": assignment_name,
                    "course_id": course_id,
                    "lms_user_id": lms_user_id,
                    "user_role": user_role,
                },  # noqa: E231
            }

            self.log.debug("Returning authentiation dictionary with %s" % auth_dict)

            return auth_dict
