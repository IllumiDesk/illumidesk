import pytest
from app import create_app
from app import db
from app.models import GraderService


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture(scope="module")
def new_service():
    # Create an initial test service object
    service = GraderService(
        "my-service",
        "test-course-100",
        "http://grader-my-service:8888",
        "test-api-token",
    )
    return service


@pytest.fixture(scope="module")
def client():
    app = create_app("flask_test.cfg")

    # Create a test client using the Flask application configured for testing
    with app.client() as test_client:
        # Establish an application context
        with app.app_context():
            yield client


@pytest.fixture(scope="module")
def init_database(test_client):
    # Create the database and the database table
    db.create_all()

    # Insert service data
    service1 = GraderService(
        "my-service1",
        "test-course-101",
        "http://grader-my-service1:8888",
        "test-api-token1",
    )
    service2 = GraderService(
        "my-service2",
        "test-course-102",
        "http://grader-my-service2:8888",
        "test-api-token2",
    )
    db.session.add(service1)
    db.session.add(service2)

    # Commit the changes for the services
    db.session.commit()

    yield

    # Drop records after testing completes
    db.drop_all()
