import pytest

from illumidesk.apis.jupyterhub_api import JupyterHubAPI


def test_initializer_set_http_client():
    """
    Does initializer set a httpclient instance?
    """
    
    sut = JupyterHubAPI()
    assert sut.client is not None

def test_initializer_set_api_token():
    """
    Does initializer set a httpclient instance?
    """
    
    sut = JupyterHubAPI()
    assert sut.client is not None

@pytest.mark.asyncio
async def test_create_group_raise_error_with_group_empty():
    """
    Does create_group method accept a group_name empty?
    """
    with pytest.raises(ValueError):
        await JupyterHubAPI().create_group('')
