from typing import Any
from typing import Dict

from jupyterhub.app import JupyterHub
from jupyterhub.auth import Authenticator
from jupyterhub.handlers import BaseHandler

from .handlers import IllumiDeskDummyLoginHandler
from .validators import IllumiDeskDummyAuthenticatorValidator


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
        return [("/login", IllumiDeskDummyLoginHandler)]

    async def authenticate(  # noqa: C901
        self, handler: BaseHandler, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:  # noqa: C901
        """Allow any user/pass combo"""

        validator = IllumiDeskDummyAuthenticatorValidator()

        # extract the request arguments to a dict
        args = {}
        for k, values in data.items():
            args[k] = values[0].decode()
        self.log.debug("Decoded args from request: %s" % args)

        if validator.validate_login_request(args):
            # get the lms vendor to implement optional logic for said vendor
            username = data["username"]
            assignment_name = data["assignment_name"]
            course_id = data["course_id"]
            lms_user_id = data["lms_user_id"]
            user_role = data["user_role"]

            return {
                "name": username,
                "auth_state": {
                    "assignment_name": assignment_name,
                    "course_id": course_id,
                    "lms_user_id": lms_user_id,
                    "user_role": user_role,
                },  # noqa: E231
            }
