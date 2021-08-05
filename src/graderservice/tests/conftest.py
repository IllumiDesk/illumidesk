import logging
import os
import unittest

import pytest
import urllib3
from graderservice import create_app
from graderservice.models import GraderService
from graderservice.models import db
from kubernetes.client.configuration import Configuration
from kubernetes.config import kube_config

DEFAULT_E2E_HOST = "127.0.0.1"


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
    monkeypatch.setenv("ILLUMIDESK_K8S_NAMESPACE", "test")
    monkeypatch.setenv("ILLUMIDESK_MNT_ROOT", "/illumidesk-courses")
    monkeypatch.setenv("ILLUMIDESK_NB_EXCHANGE_MNT_ROOT", "/illumidesk-nb-exchange")
    monkeypatch.setenv("GRADER_EXCHANGE_SHARED_PVC", "exchange-shared-volume")
    monkeypatch.setenv("GRADER_IMAGE_NAME", "illumidesk/grader-notebook:latest")
    monkeypatch.setenv("GRADER_IMAGE_PULL_POLICY", "IfNotPresent")
    monkeypatch.setenv("GRADER_PVC", "grader-setup-pvc")
    monkeypatch.setenv("GRADER_REQUESTS_MEM", "")
    monkeypatch.setenv("GRADER_REQUESTS_CPU", "")
    monkeypatch.setenv("GRADER_LIMITS_MEM", "500Mi")
    monkeypatch.setenv("GRADER_LIMITS_CPU", "1000m")
    monkeypatch.setenv("GRADER_SHARED_PVC", "exchange-shared-volume")
    monkeypatch.setenv("IS_DEBUG", "True")
    monkeypatch.setenv("MNT_ROOT", "/illumidesk-courses")
    monkeypatch.setenv("NB_UID", "10001")
    monkeypatch.setenv("NB_GID", "100")


@pytest.fixture(scope="function")
def mock_kube_deployment(kubeconfig, kube, grader_setup_environ):
    """Creates a test kubernetes deployment"""
    course_id = "intro101"
    org_name = "acme"
    sub_path_grader_home = f"/home/grader-{course_id}"
    sub_path_exchange = f"/illumidesk-nb-exchange/{org_name}/exchange"

    # define the container to launch
    container = kube.V1Container(
        name="grader-notebook",
        image="illumidesk/grader-notebook:latest",
        command=["start-notebook.sh", f"--group=formgrade-{course_id}"],
        ports=[kube.V1ContainerPort(container_port=8888)],
        working_dir=f"/home/grader-{course_id}",
        resources=kube.V1ResourceRequirements(
            requests={
                "cpu": os.environ.get("GRADER_REQUESTS_CPU"),
                "memory": os.environ.get("GRADER_REQUESTS_MEM"),
            },
            limits={
                "cpu": os.environ.get("GRADER_LIMITS_CPU"),
                "memory": os.environ.get("GRADER_LIMITS_MEM"),
            },
        ),
        security_context=kube.V1SecurityContext(allow_privilege_escalation=False),
        env=[
            kube.V1EnvVar(name="DEBUG", value=os.environ.get("IS_DEBUG")),
            kube.V1EnvVar(
                name="JUPYTERHUB_SERVICE_NAME",
                value=os.environ.get("JUPYTERHUB_SERVICE_NAME"),
            ),
            kube.V1EnvVar(
                name="JUPYTERHUB_API_TOKEN",
                value=os.environ.get("JUPYTERHUB_API_TOKEN"),
            ),
            # we're using the K8s Service name 'hub' (defined in the jhub helm chart)
            # to connect from our grader-notebooks
            kube.V1EnvVar(
                name="JUPYTERHUB_API_URL", value=os.environ.get("JUPYTERHUB_API_URL")
            ),
            kube.V1EnvVar(
                name="JUPYTERHUB_BASE_URL", value=os.environ.get("JUPYTERHUB_BASE_URL")
            ),
            kube.V1EnvVar(
                name="JUPYTERHUB_SERVICE_PREFIX",
                value=f"/services/{course_id}/",
            ),
            kube.V1EnvVar(name="JUPYTERHUB_CLIENT_ID", value=f"service-{course_id}"),
            kube.V1EnvVar(
                name="JUPYTERHUB_USER", value=os.environ.get("JUPYTERHUB_USER")
            ),
            kube.V1EnvVar(name="NB_UID", value=os.environ.get("NB_UID")),
            kube.V1EnvVar(name="NB_GID", value=os.environ.get("NB_GID")),
            kube.V1EnvVar(name="NB_USER", value=os.environ.get("NB_USER")),
        ],
        volume_mounts=[
            kube.V1VolumeMount(
                mount_path=f"/home/grader-{course_id}",
                name="grader-setup-pvc",
                sub_path=sub_path_grader_home,
            ),
            kube.V1VolumeMount(
                mount_path="/srv/nbgrader/exchange",
                name="exchange-shared-volume",
                sub_path=sub_path_exchange,
            ),
        ],
    )
    # Create and configure a spec section
    template = kube.V1PodTemplateSpec(
        metadata=kube.V1ObjectMeta(
            labels={"component": "grader-intro101", "app": "illumidesk"}
        ),
        spec=kube.V1PodSpec(
            containers=[container],
            security_context=kube.V1PodSecurityContext(run_as_user=0),
            volumes=[
                kube.V1Volume(
                    name="grader-setup-pvc",
                    persistent_volume_claim=kube.V1PersistentVolumeClaimVolumeSource(
                        claim_name="grader-setup-pvc"
                    ),
                ),
                kube.V1Volume(
                    name="exchange-shared-volume",
                    persistent_volume_claim=kube.V1PersistentVolumeClaimVolumeSource(
                        claim_name="exchange-shared-volume"
                    ),
                ),
            ],
        ),
    )
    # Create the specification of deployment
    spec = kube.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector={"matchLabels": {"component": course_id}},
    )
    # Instantiate the deployment object
    deployment = kube.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=kube.V1ObjectMeta(name=course_id),
        spec=spec,
    )

    return deployment


@pytest.fixture(scope="session")
def get_kube_configuration():
    config = Configuration()
    config.host = None
    if os.path.exists(os.path.expanduser(kube_config.KUBE_CONFIG_DEFAULT_LOCATION)):
        kube_config.load_kube_config(client_configuration=config)
    else:
        print(
            "Unable to load config from %s" % kube_config.KUBE_CONFIG_DEFAULT_LOCATION
        )
        for url in [
            "https://%s:8443" % DEFAULT_E2E_HOST,
            "http://%s:8080" % DEFAULT_E2E_HOST,
        ]:
            try:
                urllib3.PoolManager().request("GET", url)
                config.host = url
                config.verify_ssl = False
                urllib3.disable_warnings()
                break
            except urllib3.exceptions.HTTPError:
                pass
    if config.host is None:
        raise unittest.SkipTest("Unable to find a running Kubernetes instance")
    config.assert_hostname = False
    return config
