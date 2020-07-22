import os
import sys

import requests

from illumidesk.authenticators.authenticator import LTI11Authenticator
from illumidesk.authenticators.authenticator import setup_course_hook
from illumidesk.grades.handlers import SendGradesHandler
from illumidesk.spawners.spawners import IllumiDeskRoleDockerSpawner
from illumidesk.spawners.spawners import IllumiDeskWorkSpaceDockerSpawner  # noqa: F401


c = get_config()

# FIRST load the base configuration file (with common settings)
load_subconfig('/etc/jupyterhub/jupyterhub_config_base.py')
# THEN override the settings that apply only with LT13 authentication type

##########################################
# BEGIN JUPYTERHUB APPLICATION
##########################################
# LTI 1.1 authenticator class.
c.JupyterHub.authenticator_class = LTI11Authenticator
# Spawn containers with by role or workspace type
c.JupyterHub.spawner_class = IllumiDeskRoleDockerSpawner
# c.JupyterHub.spawner_class = IllumiDeskWorkSpaceDockerSpawner
##########################################
# END JUPYTERHUB APPLICATION
##########################################

##########################################
# BEGIN LTI 1.1 AUTHENTICATOR
##########################################
c.LTIAuthenticator.consumers = {
    os.environ.get('LTI_CONSUMER_KEY')
    or 'ild_test_consumer_key': os.environ.get('LTI_SHARED_SECRET')
    or 'ild_test_shared_secret'
}
# Custom Handlers
# the first one is used to send grades to LMS
# this url pattern was changed to accept spaces in the assignment name
c.JupyterHub.extra_handlers = [
    (r'/submit-grades/(?P<course_id>[a-zA-Z0-9-_]+)/(?P<assignment_name>.*)$', SendGradesHandler,),
]
##########################################
# END LTI 1.1 AUTHENTICATOR
##########################################

##########################################
# BEGIN GENERAL AUTHENTICATION
##########################################
# Post auth hook to setup course
c.Authenticator.post_auth_hook = setup_course_hook
# If using an authenticator which requires additional logic,
# set to True.
c.Authenticator.enable_auth_state = True
##########################################
# END GENERAL AUTHENTICATION
##########################################

##########################################
# SETUP COURSE SERVICE
##########################################
# Dynamic config to setup new courses

# course setup service name
service_name = os.environ.get('DOCKER_SETUP_COURSE_SERVICE_NAME') or 'setup-course'

# course setup service port
port = os.environ.get('DOCKER_SETUP_COURSE_PORT') or '8000'

# get the response from course setup app endpoint
response = requests.get(f'http://{service_name}:{port}/config')

# store course setup configuration
config = response.json()

# load k/v's when starting jupyterhub
c.JupyterHub.load_groups.update(config['load_groups'])
c.JupyterHub.services.extend(config['services'])

##########################################
# END SETUP COURSE SERVICE
##########################################
