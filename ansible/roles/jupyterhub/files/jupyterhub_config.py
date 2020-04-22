import asyncio
import json
import logging
import os
import pwd
import re
import shutil
import requests

from illumidesk.spawners.spawner import IllumiDeskDockerSpawner

c = get_config()

##########################################
# BEGIN JUPYTERHUB APPLICATION
##########################################

# Set to debug for testing
c.JupyterHub.log_level = 'DEBUG'

# Allows multiple single-server per user
c.JupyterHub.allow_named_servers = False

# Load data files
c.JupyterHub.data_files_path = '/usr/local/share/jupyterhub/'

# Use custom logo
c.JupyterHub.logo_file = os.path.join(
    '/usr/local/share/jupyterhub/', 'static', 'images', 'illumidesk-80.png'
)

# Template files
c.JupyterHub.template_paths = ('/usr/local/share/jupyterhub/templates',)

# Allow the hub to listen on any ip address
c.JupyterHub.hub_ip = '0.0.0.0'

# This is usually the hub container's name
c.JupyterHub.hub_connect_ip = 'jupyterhub'

# Provide iframe support
c.JupyterHub.tornado_settings = {
    "headers": {"Content-Security-Policy": "frame-ancestors 'self' *"}
}

# Load data files
c.JupyterHub.data_files_path = '/usr/local/share/jupyterhub/'

# Persist hub cookie secret on volume mounted inside container
data_dir = '/data'

c.JupyterHub.cookie_secret_file = os.path.join(data_dir, 'jupyterhub_cookie_secret')

# The instructor1 and instructor2 users have access to different shared
# grader notebooks. bitdiddle, hacker, and reasoner students are from
# the `nbgrader quickstart <course name>` command.
c.JupyterHub.load_groups = {
    os.environ.get('DEMO_INSTRUCTOR_GROUP'): [
        'instructor1',
        'instructor2',
        os.environ.get('DEMO_GRADER_NAME'),
    ],
    os.environ.get('DEMO_STUDENT_GROUP'): [
        'student1',
        'bitdiddle',
        'hacker',
        'reasoner',
    ],
}

# Allow admin access to end-user notebooks
c.JupyterHub.admin_access = True

# Start the grader notebook as a service. The port can be whatever you want
# and the group has to match the name of the DEMO_GRADER_NAME group defined above.
# The cull_idle service conserves resources.
course_id = os.environ.get('COURSE_ID')
c.JupyterHub.services = [
    {
        'name': os.environ.get('COURSE_ID'),
        'url': f'http://{course_id}:8888',
        'oauth_no_confirm': True,
        'admin': True,
        'api_token': os.environ.get('JUPYTERHUB_API_TOKEN'),
    },
    {
        'name': 'cull_idle',
        'admin': True,
        'command': 'python3 /srv/jupyterhub/cull_idle_servers.py --timeout=3600'.split(),
        'api_token': os.environ.get('JUPYTERHUB_API_TOKEN'),
    },
]

# Refrain from cleaning up servers when restarting the hub
c.JupyterHub.cleanup_servers = False

# JupyterHub postgres settings
c.JupyterHub.db_url = 'postgresql://{user}:{password}@{host}/{db}'.format(
    user=os.environ.get('POSTGRES_USER'),
    password=os.environ.get('POSTGRES_PASSWORD'),
    host=os.environ.get('POSTGRES_HOST'),
    db=os.environ.get('POSTGRES_DB'),
)

# User authentication class
# c.JupyterHub.authenticator_class = 'firstuseauthenticator.FirstUseAuthenticator'

# LTI 1.1 authenticator class.
c.JupyterHub.authenticator_class = 'illumidesk.authenticators.authenticator.LTI11Authenticator'

# Spawn containers with custom dockerspawner class
c.JupyterHub.spawner_class = IllumiDeskDockerSpawner

##########################################
# END JUPYTERHUB APPLICATION
##########################################

##########################################
# BEGIN REVERSE PROXY
##########################################

# Use an external service to manage the proxy
from jupyterhub_traefik_proxy import TraefikTomlProxy

# configure JupyterHub to use TraefikTomlProxy
c.JupyterHub.proxy_class = TraefikTomlProxy

# mark the proxy as externally managed
c.TraefikTomlProxy.should_start = False

c.TraefikProxy.traefik_api_url = 'http://reverse-proxy:8099'

# traefik api endpoint login password
c.TraefikTomlProxy.traefik_api_password = "admin"

# traefik api endpoint login username
c.TraefikTomlProxy.traefik_api_username = "api_admin"

# traefik's dynamic configuration file
c.TraefikTomlProxy.toml_dynamic_config_file = "/etc/traefik/rules.toml"


##########################################
# END REVERSE PROXY
##########################################

##########################################
# BEGIN FIRSTUSE AUTHENTICATION
##########################################

# Our user list for demos when using FirstUseAuthenticator. Uncomment and add initial
# users as needed. This avoids having the login form which accepts any username/password
# c.Authenticator.whitelist = [
#     'admin',
#     'instructor1',
#     'instructor2',
#     'student1',
#     'bitdiddle',
#     'hacker',
#     'reasoner',
#     os.environ.get('DEMO_GRADER_NAME'),
# ]

# Refrain from creating users within the JupyterHub container
# c.FirstUseAuthenticator.create_users = False

##########################################
# END FIRSTUSE AUTHENTICATION
##########################################

##########################################
# BEGIN LTI 1.1 AUTHENTICATOR
##########################################

c.LTIAuthenticator.consumers = {
    os.environ.get('LTI_CONSUMER_KEY')
    or 'consumer_key': os.environ.get('LTI_SHARED_SECRET')
    or 'shared_secret'
}

##########################################
# END LTI 1.1 AUTHENTICATOR
##########################################

##########################################
# BEGIN GENERAL AUTHENTICATION
##########################################

# Add other admin users as needed
c.Authenticator.admin_users = {
    'admin',
    os.environ.get('DEMO_INSTRUCTOR_NAME'),
}

# If using an authenticator which requires additional logic,
# set to True.
c.Authenticator.enable_auth_state = False

##########################################
# END GENERAL AUTHENTICATION
##########################################

##########################################
# BEGIN GENERAL SPAWNER
##########################################

# Limit memory
c.Spawner.mem_limit = '1G'

##########################################
# END GENERAL SPAWNER
##########################################

##########################################
# BEGIN CUSTOM DOCKERSPAWNER
##########################################

# Allow container to use any ip address
c.DockerSpawner.host_ip = '0.0.0.0'

spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD') or 'start-singleuser.sh'
c.DockerSpawner.extra_create_kwargs.update({'command': spawn_cmd})

# Tell the user containers to connect to our docker network
network_name = os.environ.get('DOCKER_NETWORK_NAME') or 'jupyter-network'
c.DockerSpawner.network_name = network_name

# Remove containers when stopping the hub
c.DockerSpawner.remove_containers = True
c.DockerSpawner.remove = True

# Notebook image name
notebook_image_name = os.environ.get('NOTEBOOK_IMAGE_NAME') or 'jupyterhub-user'

# nbgrader exchange directory
exchange_dir = os.environ.get('EXCHANGE_DIR') or '/srv/nbgrader/exchange'

# Organization name
org_name = os.environ.get('ORGANIZATION_NAME') or 'my-org'

# Notebook directory within docker image
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR')

# Root directory to mount org, home, and exchange folders
mnt_root = os.environ.get('MNT_ROOT')

# Mount volumes
c.DockerSpawner.volumes = {
    f'{mnt_root}/{org_name}' + '/home/{username}': notebook_dir,
    f'{mnt_root}/{org_name}/exchange': exchange_dir,
}

##########################################
# END CUSTOM DOCKERSPAWNER
##########################################

# Dynamic config to setup new courses

if c.JupyterHub.authenticator_class == 'illumidesk.authenticators.authenticator.LTI11Authenticator':

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
