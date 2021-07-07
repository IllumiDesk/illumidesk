import os
from typing import Dict
from unittest.mock import Mock

import pytest
from jupyterhub.tests.mocking import MockHub
from tornado.httputil import HTTPServerRequest
from tornado.web import Application
from tornado.web import RequestHandler


@pytest.fixture
def app():
    hub = MockHub()
    hub.init_db()
    return hub


@pytest.fixture(scope="module")
def auth_state_dict():
    authenticator_auth_state = {
        "name": "student1",
        "auth_state": {
            "assignment_" "course_id": "intro101",
            "lms_user_id": "abc123",
            "user_role": "Learner",
        },
    }
    return authenticator_auth_state


@pytest.fixture(scope="function")
def make_dummy_authentication_request_args() -> Dict[str, bytes]:
    """Creates a request to emulate a login request.

    Returns:
        Dict[str, bytes]: Authenticator dictionary
    """

    def _make_dummy_authentication_request_args():
        args = {
            "username": ["foobar".encode()],
            "password": ["mypassword".encode()],
            "assignment_name": ["lab101".encode()],
            "course_id": ["intro101".encode()],
            "lms_user_id": ["abc123".encode()],
            "user_role": ["Student".encode()],
        }

        return args

    return _make_dummy_authentication_request_args


@pytest.fixture(scope="function")
def make_mock_request_handler() -> RequestHandler:
    """
    Sourced from https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/tests/mocks.py
    """

    def _make_mock_request_handler(
        handler: RequestHandler,
        uri: str = "https://hub.example.com",
        method: str = "GET",
        **settings: dict,
    ) -> RequestHandler:
        """Instantiate a Handler in a mock application"""
        application = Application(
            hub=Mock(
                base_url="/hub/",
                server=Mock(base_url="/hub/"),
            ),
            cookie_secret=os.urandom(32),
            db=Mock(rollback=Mock(return_value=None)),
            **settings,
        )
        request = HTTPServerRequest(
            method=method,
            uri=uri,
            connection=Mock(),
        )
        handler = RequestHandler(
            application=application,
            request=request,
        )
        handler._transforms = []
        return handler

    return _make_mock_request_handler
