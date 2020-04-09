import os
import shutil
import sys
import logging
from pathlib import Path
from secrets import token_hex

import docker

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Course:
    """
    Class to manage new course setups.

    Attributes:
        org: Organization name used in the account's sub-domain
        course_id: The normalized course id. Must not contain more than
        30 characters or have special characters.
        domain: Domain name from tool consumer that launched the request
        exchange_root: Path for exchange folder
        grader_name: Grader's account name
        grader_root: Grader's home path
        course_root: Course's root path
        token: JupyterHub API token used to authenticat requests with the Hub
        jupyterhub_lock: Lock file to manage jupyterhub_config.py
        uid: Grader's user id
        gid: Grader's group id
        is_new_setup: True indicates a new setup, False otherwise
    """
    def __init__(self, *, org: str, course_id: str, domain: str):
        self.org = org
        self.course_id = course_id
        self.domain = domain
        self.exchange_root = Path(os.environ.get('NFS_ROOT'), self.org, 'exchange')
        self.grader_name = f'grader-{course_id}'
        self.grader_root = Path(
            os.environ.get('NFS_ROOT'),
            org,
            'home',
            self.grader_name,
        )
        self.course_root = self.grader_root / course_id
        self.token = token_hex(32)
        self.client = docker.from_env()
        self.jupyterhub_lock = os.environ.get('JUPYTERHUB_CONFIG_PATH') + '/jhub.lock'
        self.uid = int(os.environ.get('NB_UID'))
        self.gid = int(os.environ.get('NB_GID'))
        self.is_new_setup = False

    def should_setup(self):
        """
        If the grader container exists then the setup_course boolean is set to
        false, otherwise true.

        Raises:
            docker.errors.NotFound
        """
        try:
            self.client.containers.get(self.grader_name)
            logger.debug('Grader container exists %s' % self.grader_name)
        except docker.errors.NotFound:
            logger.error('Grader container not found')
            self.is_new_setup = True
            return True
        
        return False

    def setup(self):
        """
        Function to bootstrap new course setup
        
        Returns:
            is_new_setup: boolean to indicate whether or not the this setup
            function executed the functions to set up a new course.
        """
        if self.should_setup():
            self.create_directories()
            self.add_jupyterhub_grader_group()
            self.add_jupyterhub_student_group()
            self.run()
            self.update_jupyterhub_config()
        return self.is_new_setup

    def create_directories(self):
        """
        Creates exchange, grader account, and course directories as well
        as nbgrader configuration files. All directories and files are updated to have the
        UID/GID that belong to the instructor/grader values. Students and Grader/Instructors
        should have different UID's but the same GID.
        """
        logger.debug('Creating exchange directory %s' % self.exchange_root)
        self.exchange_root.mkdir(parents=True, exist_ok=True)
        self.exchange_root.chmod(0o777)
        self.course_root.mkdir(parents=True, exist_ok=True)
        logger.debug(
            'Creating grader directory and permissions with path %s to %s:%s ' %  
            (self.grader_root,
            self.uid,
            self.gid)
        )
        shutil.chown(str(self.grader_root), user=self.uid, group=self.gid)
        logger.debug(
            'Changing course directory permissions with path %s to %s:%s ' %
            (self.course_root,
            self.uid,
            self.gid)
        )
        shutil.chown(str(self.course_root), user=self.uid, group=self.gid)
        jupyter_config_path = self.grader_root / '.jupyter'
        logger.debug('Course jupyter config path %s' % jupyter_config_path)
        jupyter_config_path.mkdir(parents=True, exist_ok=True)
        shutil.chown(str(jupyter_config_path), user=self.uid, group=self.gid)
        logger.debug('Change course jupyter config permissions to %s:%s' % (self.uid, self.gid))
        nbgrader_config_path = jupyter_config_path / 'nbgrader_config.py'
        logger.debug('Course nbgrader_config.py path %s' % nbgrader_config_path)
        nbgrader_config = NB_GRADER_CONFIG_TEMPLATE.format(
            grader_name=self.grader_name,
            course_id=self.course_id
        )
        nbgrader_config_path.write_text(nbgrader_config)
        shutil.chown(str(nbgrader_config_path), user=self.uid, group=self.gid)
        logger.debug('Added nbgrader config %s with permissions %s:%s' %
            (nbgrader_config,
            self.uid,
            self.gid)
        )

    def add_jupyterhub_grader_group(self):
        """
        Add formgrader group with JupyterHub's REST API by sending a 
        POST request to the the endpoint ../groups/formgrade-{course_id}.

        Returns:
            Response from JupyterHub's add group endpoint
        """
        logger.debug('Adding grader group formgrade-%s with JupyterHub REST API' % self.course_id)
        jupyterhub_api_url = os.environ.get('JUPYTERHUB_API_URL')
        token = os.environ.get('JUPYTERHUB_API_TOKEN')
        response = requests.post(f'{jupyterhub_api_url}/groups/formgrade-{self.course_id}',
            headers={
                    'Authorization': f'token {token}',
            }
        )
        logger.debug('Response object when adding formgrader group: %s' % response.json())
        return response.json()

    def add_jupyterhub_student_group(self):
        """
        Add nbgrader group with JupyterHub's REST API by sending a 
        POST request to the the endpoint ../groups/nbgrader-{course_id}.

        Returns:
            Response from JupyterHub's add group endpoint
        """
        logger.debug('Adding student group nbgrader-%s with JupyterHub REST API' % self.course_id)
        jupyterhub_api_url = os.environ.get('JUPYTERHUB_API_URL')
        logger.debug('Adding student group by posting to %s' % jupyterhub_api_url)
        token = os.environ.get('JUPYTERHUB_API_TOKEN')
        logger.debug('Using token %s to add student group' % token)
        response = requests.post(f'{jupyterhub_api_url}/groups/nbgrader-{self.course_id}',
            headers={
                    'Authorization': f'token {token}',
            }
        )
        logger.debug('Adding group nbgrader-%s' % self.course_id)
        logger.debug('Response object when adding nbgrader group: %s' % response.json())
        return response.json()

    def run(self):
        """
        Create and run a grader notebook with the docker client. This service's settings
        should coincide with the grader's JupyterHub.services definition. The JupyterHub.service
        is defined as an externally managed service and the docker client is what manages this 
        grader service.
        """
        logger.debug('Running grader container with exchange root %s' % self.exchange_root)
        jupyterhub_api_url = os.environ.get('JUPYTERHUB_API_URL')
        jupyterhub_api_token = os.environ.get('JUPYTERHUB_API_TOKEN')
        logger.debug('Grader container JUPYTERHUB_API_URL set to %s' % jupyterhub_api_url)
        logger.debug('Grader container JUPYTERHUB_API_TOKEN set to %s' % jupyterhub_api_token)
        self.client.containers.run(
            detach=True,
            image=os.environ.get('GRADER_SERVICE_IMAGE'),
            command=['start-notebook.sh', f'--group=formgrade-{self.course_id}'],
            environment=[
                f'JUPYTERHUB_SERVICE_NAME={self.course_id}',
                f'JUPYTERHUB_API_TOKEN={self.token}',
                f'JUPYTERHUB_API_URL={jupyterhub_api_url}',
                f'JUPYTERHUB_BASE_URL=https://{self.domain}/',
                f'JUPYTERHUB_SERVICE_PREFIX=/services/{self.course_id}',
                f'JUPYTERHUB_CLIENT_ID=service-{self.course_id}',
                f'JUPYTERHUB_USER={self.grader_name}',
                f'NB_UID={self.uid}',
                f'NB_GID={self.gid}',
                f'NB_USER={self.grader_name}',
            ],
            volumes={
                str(self.grader_root): {'bind': f'/home/{self.grader_name}'},
                str(self.exchange_root): {'bind': '/srv/nbgrader/exchange'},
            },
            name=self.grader_name,
            user='root',
            working_dir=f'/home/{self.grader_name}',
            network=os.environ.get('DOCKER_NETWORK'),
            restart_policy={'Name': 'on-failure', 'MaximumRetryCount': 5}
        )

    def update_jupyterhub_config(self):
        """
        We can add groups and users with the REST API, but not services. Therefore
        add new services to the JupyterHub.services section within the jupyterhub 
        configuration file (jupyterhub_config.py).
        """
        jupyterhub_config_json = Path(JSON_FILE_PATH)
        url = f'http://{self.grader_name}:8888'
        service_config = {
            'name': self.course_id,
            'url': url,
            'oauth_no_confirm': True,
            'admin': True,
            'api_token': self.token
        }
        load_group = {f'formgrade-{self.course_id}': [self.grader_name]}
        if not any(s for s in cache['services'] if s['url'] == service_config['url']):
            cache['services'].append(service_config)
        cache['load_groups'].update(load_group)
        lock = FileLock(str(self.jupyterhub_lock))
        with lock:
            with jupyterhub_config_json.open('r+') as config:
                json.dump(cache, config)