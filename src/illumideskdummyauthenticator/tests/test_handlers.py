import pytest
from illumideskdummyauthenticator.authenticator import IllumiDeskDummyAuthenticator


@pytest.mark.asyncio
async def test_handlers(app):
    """Test if all handlers are available on the Authenticator"""
    auth = IllumiDeskDummyAuthenticator()
    handlers = auth.get_handlers(app)
    assert handlers[0][0] == "/login"
