import os

from illumidesk.apis.setup_course_service import get_current_service_definitions
from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.authenticators.authenticator import setup_course_hook
from illumidesk.authenticators.handlers import LTI13LoginHandler

from illumidesk.grades.handlers import SendGradesHandler

from illumidesk.lti13.handlers import LTI13ConfigHandler
from illumidesk.lti13.handlers import LTI13JWKSHandler

from illumidesk.spawners.spawners import IllumiDeskRoleDockerSpawner

c = get_config()


# load the base configuration file (with common settings)
load_subconfig('/etc/jupyterhub/jupyterhub_config_base.py')  # noqa: F821

##########################################
# BEGIN LTI 1.3 AUTHENTICATOR
##########################################

# LTI 1.3 authenticator class.
c.JupyterHub.authenticator_class = LTI13Authenticator

# Spawn containers with by role
c.JupyterHub.spawner_class = IllumiDeskRoleDockerSpawner

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
    (r'/lti/launch$', LTI13LoginHandler),
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

##########################################
# END GENERAL AUTHENTICATION
##########################################

##########################################
# SETUP COURSE SERVICE
##########################################

# Dynamic config to setup new courses
extra_services = get_current_service_definitions()

# load k/v's when starting jupyterhub
c.JupyterHub.load_groups.update(extra_services['load_groups'])
c.JupyterHub.services.extend(extra_services['services'])

##########################################
# END SETUP COURSE SERVICE
##########################################
