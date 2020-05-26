import pytest
import uuid

@pytest.fixture(scope="function")
def jupyterhub_api_environ(monkeypatch):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv('JUPYTERHUB_API_TOKEN', str(uuid.uuid4()))
    monkeypatch.setenv('JUPYTERHUB_API_URL', 'localhost/hub/api')