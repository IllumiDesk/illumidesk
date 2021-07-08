import pytest
from illumideskdummyauthenticator.authenticator import IllumiDeskDummyAuthenticator


@pytest.mark.asyncio
async def test_handlers(hubapp):
    """Test if all handlers are available on the Authenticator"""
    auth = IllumiDeskDummyAuthenticator()
    handlers = auth.get_handlers(hubapp)
    assert handlers[0][0] == "/dummy/login"
