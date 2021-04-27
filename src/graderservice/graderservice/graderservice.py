import logging
import logging.config
import os
import shutil
from datetime import datetime
from os import path
from pathlib import Path
from secrets import token_hex

from graderservice.templates import NBGRADER_COURSE_CONFIG_TEMPLATE
from graderservice.templates import NBGRADER_HOME_CONFIG_TEMPLATE
from kubernetes import client
from kubernetes import config
from kubernetes.config import ConfigException

log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging_config.ini")
logging.config.fileConfig(log_file_path)
logger = logging.getLogger()

logging.getLogger("asyncio").setLevel(logging.WARNING)


# namespace to deploy new pods
NAMESPACE = os.environ.get("ILLUMIDESK_K8S_NAMESPACE", "default")
# image name for grader-notebooks
GRADER_IMAGE_NAME = os.environ.get(
    "GRADER_IMAGE_NAME", "illumidesk/grader-notebook:latest"
)
# mount root path for grader and course home directories
MNT_ROOT = os.environ.get("ILLUMIDESK_MNT_ROOT", "/illumidesk-courses")
# shared directory to use with students and instructors
EXCHANGE_MNT_ROOT = os.environ.get(
    "ILLUMIDESK_NB_EXCHANGE_MNT_ROOT", "/illumidesk-nb-exchange"
)
GRADER_PVC = os.environ.get("GRADER_PVC", "grader-setup-pvc")
GRADER_EXCHANGE_SHARED_PVC = os.environ.get(
    "GRADER_SHARED_PVC", "exchange-shared-volume"
)

# user UI and GID to use within the grader container
NB_UID = os.environ.get("NB_UID", 10001)
NB_GID = os.environ.get("NB_GID", 100)

# NBGrader DATABASE settings to save in nbgrader_config.py file
nbgrader_db_host = os.environ.get("POSTGRES_NBGRADER_HOST")
nbgrader_db_password = os.environ.get("POSTGRES_NBGRADER_PASSWORD")
nbgrader_db_user = os.environ.get("POSTGRES_NBGRADER_USER")
nbgrader_db_port = os.environ.get("POSTGRES_NBGRADER_PORT")
nbgrader_db_name = os.environ.get("POSTGRES_NBGRADER_DB_NAME")


class GraderServiceLauncher:
    def __init__(self, org_name: str, course_id: str, is_debug: bool = False):
        """
        Helper class to launch grader notebooks within the kubernetes cluster

        Args:
          org_name: the organization name
          course_id: the course id
          is_debug: if true, runs the grader notebook and the kubernetes client with
            debugging enabled. Defaults to False.

        Raises:
          ConfigException if the kubectl python client does not have a valid configuration set.
        """
        try:
            # try to load the cluster credentials
            # Configs can be set in Configuration class directly or using helper utility
            config.load_incluster_config()
        except ConfigException:
            # next method uses the KUBECONFIG env var by default
            config.load_kube_config()
        # Uncomment the following lines to enable debug logging
        kube_client_config = client.Configuration()
        kube_client_config.debug = is_debug
        self.apps_v1 = client.AppsV1Api(
            api_client=client.ApiClient(configuration=kube_client_config)
        )
        self.coreV1Api = client.CoreV1Api()
        self.course_id = course_id
        self.grader_is_debug = is_debug
        self.grader_name = f"grader-{self.course_id}"
        self.grader_token = token_hex(32)
        self.org_name = org_name

        # Course home directory, its parent should be the grader name
        self.course_dir = Path(
            f"{MNT_ROOT}/{self.org_name}/home/grader-{self.course_id}/{self.course_id}"
        )
        # set the exchange directory path
        self.exchange_dir = Path(EXCHANGE_MNT_ROOT, self.org_name, "exchange")

    def grader_deployment_exists(self) -> bool:
        """Check if there is a deployment for the grader service name"""
        # Filter deployments by the current namespace and a specific name (metadata collection)
        deployment_list = self.apps_v1.list_namespaced_deployment(
            namespace=NAMESPACE, field_selector=f"metadata.name={self.grader_name}"
        )
        if deployment_list and deployment_list.items:
            logger.info("Deployment exists for %s", self.grader_name)
            print("Deployment exists for %s", self.grader_name)
            return True

        return False

    def grader_service_exists(self) -> bool:
        """Check if the grader service exists"""
        # Filter deployments by the current namespace and a specific name (metadata collection)
        service_list = self.coreV1Api.list_namespaced_service(
            namespace=NAMESPACE, field_selector=f"metadata.name={self.grader_name}"
        )
        if service_list and service_list.items:
            logger.info("Service exists for %s", self.grader_name)
            print("Service exists for %s", self.grader_name)
            return True

        return False

    def create_grader_deployment(self):
        """Deploy the grader service"""
        # first create the home directories for grader/course
        try:
            self._create_exchange_directory()
            self._create_grader_directories()
            self._create_nbgrader_files()
        except Exception as e:
            msg = (
                "An error occurred trying to create directories and files for nbgrader."
            )
            logger.error(f"{msg}{e}")
            raise Exception(msg)

        # Create grader deployement
        deployment = self._create_deployment_object()
        api_response = self.apps_v1.create_namespaced_deployment(
            body=deployment, namespace=NAMESPACE
        )
        logger.info(f'Deployment created. Status="{str(api_response.status)}"')
        print(f'Deployment created. Status="{str(api_response.status)}"')
        # Create grader service
        service = self._create_service_object()
        self.coreV1Api.create_namespaced_service(namespace=NAMESPACE, body=service)

    def _create_exchange_directory(self):
        """Creates the exchange directory in the file system and sets permissions."""
        logger.info(f"Creating exchange directory {self.exchange_dir}")
        self.exchange_dir.mkdir(parents=True, exist_ok=True)
        self.exchange_dir.chmod(0o777)

    def _create_grader_directories(self):
        """
        Creates home directories with specific permissions
        Directories to create:
        - grader_root: /<org-name>/home/grader-<course-id>
        - course_root: /<org-name>/home/grader-<course-id>/<course-id>
        """
        logger.info(
            f'Create course directory "{self.course_dir}" with special permissions {NB_UID}:{NB_GID}'
        )
        self.course_dir.mkdir(parents=True, exist_ok=True)
        # change the course directory owner
        shutil.chown(str(self.course_dir), user=NB_UID, group=NB_GID)
        logger.info("Updated permissions for %s", self.course_dir)
        # change the grader-home directory owner
        shutil.chown(str(self.course_dir.parent), user=NB_UID, group=NB_GID)
        logger.info("Change grader home directory owner %s", self.course_dir)

    def _create_nbgrader_files(self):
        """Creates nbgrader configuration files used in the grader's home directory and the
        course directory located within the grader's home directory.
        """
        # create the .jupyter directory (a child of grader_root)
        jupyter_dir = self.course_dir.parent.joinpath(".jupyter")
        jupyter_dir.mkdir(parents=True, exist_ok=True)
        shutil.chown(str(jupyter_dir), user=NB_UID, group=NB_GID)
        # Write the nbgrader_config.py file at grader home directory
        grader_nbconfig_path = jupyter_dir.joinpath("nbgrader_config.py")
        logger.info(
            f"Writing the nbgrader_config.py file at jupyter directory (within the grader home): {grader_nbconfig_path}"
        )
        # write the file
        grader_home_nbconfig_content = NBGRADER_HOME_CONFIG_TEMPLATE.format(
            grader_name=self.grader_name,
            course_id=self.course_id,
            db_url=f"postgresql://{nbgrader_db_user}:{nbgrader_db_password}@{nbgrader_db_host}:5432/{self.org_name}_{self.course_id}",
        )
        grader_nbconfig_path.write_text(grader_home_nbconfig_content)
        # Write the nbgrader_config.py file at grader home directory
        course_nbconfig_path = self.course_dir.joinpath("nbgrader_config.py")
        logger.info(
            f"Writing the nbgrader_config.py file at course home directory: {course_nbconfig_path}"
        )
        # write the second file
        course_home_nbconfig_content = NBGRADER_COURSE_CONFIG_TEMPLATE.format(
            course_id=self.course_id
        )
        course_nbconfig_path.write_text(course_home_nbconfig_content)

    def _create_service_object(self):
        """Creates the grader setup service as a valid kubernetes service for persistence.

        Returns:
            V1Service: a kubernetes service object that represents the grader service
        """
        service = client.V1Service(
            kind="Service",
            metadata=client.V1ObjectMeta(name=self.grader_name),
            spec=client.V1ServiceSpec(
                type="ClusterIP",
                ports=[
                    client.V1ServicePort(port=8888, target_port=8888, protocol="TCP")
                ],
                selector={"component": self.grader_name},
            ),
        )
        return service

    def _create_deployment_object(self):
        """Creates the deployment object for the grader service using environment variables

        Returns:
          V1Deployment: a valid kubernetes deployment object
        """
        # Configureate Pod template container
        # Volumes to mount as subPaths of PV
        sub_path_grader_home = str(self.course_dir.parent).strip("/")
        sub_path_exchange = str(self.exchange_dir.relative_to(EXCHANGE_MNT_ROOT))
        # define the container to launch
        container = client.V1Container(
            name="grader-notebook",
            image=GRADER_IMAGE_NAME,
            command=["start-notebook.sh", f"--group=formgrade-{self.course_id}"],
            ports=[client.V1ContainerPort(container_port=8888)],
            working_dir=f"/home/{self.grader_name}",
            resources=client.V1ResourceRequirements(
                requests={"cpu": "100m", "memory": "200Mi"},
                limits={"cpu": "500m", "memory": "1G"},
            ),
            security_context=client.V1SecurityContext(allow_privilege_escalation=False),
            env=[
                client.V1EnvVar(name="DEBUG", value=self.grader_is_debug),
                client.V1EnvVar(name="JUPYTERHUB_SERVICE_NAME", value=self.course_id),
                client.V1EnvVar(name="JUPYTERHUB_API_TOKEN", value=self.grader_token),
                # we're using the K8s Service name 'hub' (defined in the jhub helm chart)
                # to connect from our grader-notebooks
                client.V1EnvVar(
                    name="JUPYTERHUB_API_URL", value="http://hub:8081/hub/api"
                ),
                client.V1EnvVar(name="JUPYTERHUB_BASE_URL", value="/"),
                client.V1EnvVar(
                    name="JUPYTERHUB_SERVICE_PREFIX",
                    value=f"/services/{self.course_id}/",
                ),
                client.V1EnvVar(
                    name="JUPYTERHUB_CLIENT_ID", value=f"service-{self.course_id}"
                ),
                client.V1EnvVar(name="JUPYTERHUB_USER", value=self.grader_name),
                client.V1EnvVar(name="NB_UID", value=str(NB_UID)),
                client.V1EnvVar(name="NB_GID", value=str(NB_GID)),
                client.V1EnvVar(name="NB_USER", value=self.grader_name),
            ],
            volume_mounts=[
                client.V1VolumeMount(
                    mount_path=f"/home/{self.grader_name}",
                    name=GRADER_PVC,
                    sub_path=sub_path_grader_home,
                ),
                client.V1VolumeMount(
                    mount_path="/srv/nbgrader/exchange",
                    name=GRADER_EXCHANGE_SHARED_PVC,
                    sub_path=sub_path_exchange,
                ),
            ],
        )
        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"component": self.grader_name, "app": "illumidesk"}
            ),
            spec=client.V1PodSpec(
                containers=[container],
                security_context=client.V1PodSecurityContext(run_as_user=0),
                volumes=[
                    client.V1Volume(
                        name=GRADER_PVC,
                        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                            claim_name=GRADER_PVC
                        ),
                    ),
                    client.V1Volume(
                        name=GRADER_EXCHANGE_SHARED_PVC,
                        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                            claim_name=GRADER_EXCHANGE_SHARED_PVC
                        ),
                    ),
                ],
            ),
        )
        # Create the specification of deployment
        spec = client.V1DeploymentSpec(
            replicas=1,
            template=template,
            selector={"matchLabels": {"component": self.grader_name}},
        )
        # Instantiate the deployment object
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=self.grader_name),
            spec=spec,
        )

        return deployment

    def delete_grader_deployment(self):
        """Deletes the grader deployment"""
        # first delete the service
        if self.grader_service_exists():
            self.coreV1Api.delete_namespaced_service(
                name=self.grader_name, namespace=NAMESPACE
            )
        # then delete the deployment
        if self.grader_deployment_exists():
            self.apps_v1.delete_namespaced_deployment(
                name=self.grader_name, namespace=NAMESPACE
            )

    def update_jhub_deployment(self):
        """Executes a patch in the jhub deployment. With this the jhub will be replaced with a new pod"""
        jhub_deployments = self.apps_v1.list_namespaced_deployment(
            namespace=NAMESPACE, label_selector="component=hub"
        )
        if jhub_deployments.items:
            # add new label with the current datetime (only used to the replacement occurs)
            for deployment in jhub_deployments.items:
                # get the jhub deployment template
                current_metadata = deployment.spec.template.metadata
                current_labels = current_metadata.labels
                # add the label
                current_labels.update(
                    {"restarted_at": datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}
                )
                current_metadata.labels = current_labels
                # update the deployment object
                deployment.spec.template.metadata = current_metadata
                api_response = self.apps_v1.patch_namespaced_deployment(
                    name="hub", namespace=NAMESPACE, body=deployment
                )
                logger.info(f"Jhub patch response:{api_response}")
                print(f"Jhub patch response:{api_response}")
