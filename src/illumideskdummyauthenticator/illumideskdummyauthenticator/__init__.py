"""
Import with 'JupyterHub.authenticator_class = illumideskdummyauthenticator.IllumiDeskDummyAuthenticator'

isort:skip_file
"""
from illumideskdummyauthenticator.authenticator import (
    IllumiDeskDummyAuthenticator,
)  # NOQA

__all__ = [IllumiDeskDummyAuthenticator]
