import os

from tornado.web import Application
from tornado.httputil import HTTPServerRequest

from unittest.mock import Mock


# sourced from https://github.com/jupyterhub/oauthenticator
def mock_handler(Handler, uri='https://hub.example.com', method='GET', **settings):
    """
    Instantiate a Handler in a mock application
    """
    application = Application(
        hub=Mock(base_url='/hub/', server=Mock(base_url='/hub/'),),
        cookie_secret=os.urandom(32),
        db=Mock(rollback=Mock(return_value=None)),
        **settings,
    )
    request = HTTPServerRequest(method=method, uri=uri, connection=Mock(),)
    handler = Handler(application=application, request=request,)
    handler._transforms = []
    return handler
