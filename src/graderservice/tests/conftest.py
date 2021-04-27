import logging

import pytest
from graderservice import create_app
from graderservice.models import GraderService
from graderservice.models import db


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    app = create_app()
    app.logger.setLevel(logging.CRITICAL)
    ctx = app.test_request_context()
    ctx.push()

    app.config["TESTING"] = True
    app.testing = True

    # This creates an in-memory sqlite db
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with app.app_context():
        db.create_all()
        service1 = GraderService(
            name="foo",
            course_id="intro101",
            url="http://intro101:8888",
            oauth_no_confirm=True,
            admin=True,
            api_token="abc123abc123",
        )
        db.session.add(service1)
        db.session.commit()

    yield app
    ctx.pop()


@pytest.fixture(scope="session")
def client(app):
    client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield client
    ctx.pop()


@pytest.fixture(scope="function")
def grader_setup_environ(monkeypatch):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv("ILLUMIDESK_K8S_NAMESPACE", "default")
    monkeypatch.setenv("ILLUMIDESK_MNT_ROOT", "/illumidesk-courses")
    monkeypatch.setenv("ILLUMIDESK_NB_EXCHANGE_MNT_ROOT", "/illumidesk-nb-exchange")
    monkeypatch.setenv("GRADER_EXCHANGE_SHARED_PVC", "exchange-shared-volume")
    monkeypatch.setenv("GRADER_IMAGE_NAME", "illumidesk/grader-notebook:latest")
    monkeypatch.setenv("GRADER_PVC", "grader-setup-pvc")
    monkeypatch.setenv("GRADER_SHARED_PVC", "exchange-shared-volume")
    monkeypatch.setenv("IS_DEBUG", "True")
    monkeypatch.setenv("MNT_ROOT", "/illumidesk-courses")
    monkeypatch.setenv("NAMESPACE", "default")
    monkeypatch.setenv("NB_UID", "10001")
    monkeypatch.setenv("NB_GID", "100")
