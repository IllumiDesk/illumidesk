import os

import requests

from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.authenticators.authenticator import setup_course_hook
from illumidesk.grades.handlers import SendGradesHandler
from illumidesk.lti13.handlers import LTI13ConfigHandler
from illumidesk.lti13.handlers import LTI13JWKSHandler
from illumidesk.spawners.spawners import IllumiDeskRoleDockerSpawner
from illumidesk.spawners.spawners import IllumiDeskWorkSpaceDockerSpawner  # noqa: F401

c = get_config()

# LTI 1.3 authenticator class.
c.JupyterHub.authenticator_class = LTI13Authenticator
# Spawn containers with by role or workspace type
c.JupyterHub.spawner_class = IllumiDeskRoleDockerSpawner
# c.JupyterHub.spawner_class = IllumiDeskWorkSpaceDockerSpawner


##########################################
# BEGIN LTI 1.3 AUTHENTICATOR
##########################################

# created after installing app in lms
c.LTI13Authenticator.client_id = os.environ.get('LTI13_CLIENT_ID')
c.LTI13Authenticator.endpoint = os.environ.get('LTI13_ENDPOINT')
c.LTI13Authenticator.token_url = os.environ.get('LTI13_TOKEN_URL')
c.LTI13Authenticator.authorize_url = os.environ.get('LTI13_AUTHORIZE_URL')

#  Custom Handlers used for LTI endpoints
# the first one is used to send grades to LMS
# this url pattern was changed to accept spaces in the assignment name
c.JupyterHub.extra_handlers = [
    (r'/submit-grades/(?P<course_id>[a-zA-Z0-9-_]+)/(?P<assignment_name>.*)$', SendGradesHandler),
    (r'/lti13/config$', LTI13ConfigHandler),
    (r'/lti13/jwks$', LTI13JWKSHandler),
]

##########################################
# END LTI 1.3 AUTHENTICATOR
##########################################

##########################################
# BEGIN GENERAL AUTHENTICATION (OVERRIDE)
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
