from typing import Any
from typing import Dict

from tornado.web import HTTPError
from traitlets.config import LoggingConfigurable

from .constants import ILLUMIDESK_DUMMY_PARAMS_REQUIRED


class IllumiDeskDummyValidator(LoggingConfigurable):
    """
    Validates that the dictionary returned by the IllumiDeskDummyAuthenticator
    has all required keys/values. Uses primarily for testing.
    """

    def validate_login_request(
        self,
        args: Dict[str, Any],
    ) -> bool:
        """
        Validate a given login request using the IllumiDesk dummy authenticator.

        Args:
          args: the request's body arguments

        Returns:
          True if the validation passes, False otherwise.

        Raises:
          HTTPError if a required argument is not inclued in the request.
        """
        # Ensure that required oauth_* body arguments are included in the request
        for param in ILLUMIDESK_DUMMY_PARAMS_REQUIRED:
            if param not in args.keys():
                raise HTTPError(400, "Required arg %s not included in request" % param)
            if not args.get(param):
                raise HTTPError(400, "Required arg %s does not have a value" % param)

        return True
