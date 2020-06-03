# Sourced from https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/tests/mocks.py
import os

from unittest.mock import Mock

from tornado.httputil import HTTPServerRequest
from tornado.web import Application
from tornado.web import RequestHandler


def mock_handler(
    handler: RequestHandler, uri: str = 'https://hub.example.com', method: str = 'GET', **settings: dict
) -> RequestHandler:
    """Instantiate a Handler in a mock application"""
    application = Application(
        hub=Mock(base_url='/hub/', server=Mock(base_url='/hub/'),),
        cookie_secret=os.urandom(32),
        db=Mock(rollback=Mock(return_value=None)),
        **settings,
    )
    request = HTTPServerRequest(method=method, uri=uri, connection=Mock(),)
    handler = RequestHandler(application=application, request=request,)
    handler._transforms = []
    return handler
