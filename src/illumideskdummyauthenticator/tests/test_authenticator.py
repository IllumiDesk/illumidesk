import json
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from illumideskdummyauthenticator.authenticator import IllumiDeskDummyAuthenticator
from illumideskdummyauthenticator.validators import IllumiDeskDummyValidator
from tornado.web import RequestHandler


@pytest.mark.asyncio
async def test_authenticator_returns_auth_state(make_dummy_authentication_request_args):
    """
    Ensure we get a valid authentication dictionary.
    """
    with patch.object(
        IllumiDeskDummyValidator, "validate_login_request", return_value=True
    ):
        authenticator = IllumiDeskDummyAuthenticator()
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(["key", "secret"])),
            request=Mock(
                arguments=make_dummy_authentication_request_args(),
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            "name": "foobar",
            "auth_state": {
                "assignment_name": "lab101",
                "course_id": "intro101",
                "lms_user_id": "abc123",
                "user_role": "Student",
            },
        }
        assert result == expected
