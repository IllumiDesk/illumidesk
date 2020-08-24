import os
import sys

from dockerspawner import DockerSpawner  # noqa: F401
from illumidesk.apis.announcement_service import ANNOUNCEMENT_JHUB_SERVICE_DEFINITION


c = get_config()

##########################################
# BEGIN JUPYTERHUB APPLICATION
##########################################

# Set to debug for teting
c.JupyterHub.log_level = 'DEBUG'

# Allows multiple single-server per user
c.JupyterHub.allow_named_servers = False

# Load data files
c.JupyterHub.data_files_path = '/usr/local/share/jupyterhub/'

# Use custom logo
c.JupyterHub.logo_file = os.path.join('/usr/local/share/jupyterhub/', 'static', 'images', 'illumidesk-80.png')

# Template files
c.JupyterHub.template_paths = ('/usr/local/share/jupyterhub/templates',)

# Allow the hub to listen on any ip address
c.JupyterHub.hub_ip = '0.0.0.0'

# This is usually the hub container's name
c.JupyterHub.hub_connect_ip = 'jupyterhub'

# Provide iframe support
c.JupyterHub.tornado_settings = {"headers": {"Content-Security-Policy": "frame-ancestors 'self' *"}}

# Load data files
c.JupyterHub.data_files_path = '/usr/local/share/jupyterhub/'

# Persist hub cookie secret on volume mounted inside container
data_dir = '/data'
c.JupyterHub.cookie_secret_file = os.path.join(data_dir, 'jupyterhub_cookie_secret')

# Allow admin access to end-user notebooks
c.JupyterHub.admin_access = True

# Refrain from cleaning up servers when restarting the hub
c.JupyterHub.cleanup_servers = False

# Define some static services that jupyterhub will manage
# Although the cull-idle service is internal, and therefore does not need an explicit
# registration of the jupyterhub api token, we add it here so the internal api client
# can use the token to utilize RESTful endpoints with full CRUD priviledges.
c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'admin': True,
        'command': [sys.executable, '-m', 'jupyterhub_idle_culler', '--timeout=3600'],
        'api_token': os.environ.get('JUPYTERHUB_API_TOKEN'),
    },
    ANNOUNCEMENT_JHUB_SERVICE_DEFINITION,
]

# JupyterHub postgres settings
c.JupyterHub.db_url = 'postgresql://{user}:{password}@{host}/{db}'.format(
    user=os.environ.get('POSTGRES_USER'),
    password=os.environ.get('POSTGRES_PASSWORD'),
    host=os.environ.get('POSTGRES_HOST'),
    db=os.environ.get('POSTGRES_DB'),
)

# Do not redirect user to his/her server (if running)
c.JupyterHub.redirect_to_server = False

# JupyterHub's base url
base_url = os.environ.get('JUPYTERHUB_BASE_URL') or ''
c.JupyterHub.base_url = base_url

# Do not redirect user to his/her server (if running)
c.JupyterHub.redirect_to_server = True

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

# indicate the proxy url to allow register new routes
c.TraefikProxy.traefik_api_url = os.environ.get('PROXY_API_URL') or 'http://reverse-proxy:8099'

# traefik api endpoint login password
c.TraefikTomlProxy.traefik_api_password = 'admin'

# traefik api endpoint login username
c.TraefikTomlProxy.traefik_api_username = 'api_admin'

# traefik's dynamic configuration file
c.TraefikTomlProxy.toml_dynamic_config_file = '/etc/traefik/rules.toml'

##########################################
# END REVERSE PROXY
##########################################

##########################################
# BEGIN GENERAL AUTHENTICATION
##########################################

admin_user = os.environ.get('JUPYTERHUB_ADMIN_USER')
# Add other admin users as needed
c.Authenticator.admin_users = {
    admin_user,
}

# If using an authenticator which requires additional logic,
# set to True.
c.Authenticator.enable_auth_state = True

##########################################
# END GENERAL AUTHENTICATION
##########################################

##########################################
# BEGIN GENERAL SPAWNER
##########################################

# Limit memory
c.Spawner.mem_limit = os.environ.get('DOCKER_SPAWN_MEM_LIMIT') or '2G'

##########################################
# END GENERAL SPAWNER
##########################################

##########################################
# BEGIN CUSTOM DOCKERSPAWNER
##########################################

# Allow container to use any ip address
c.DockerSpawner.host_ip = '0.0.0.0'

# specify the command used by the spawner to start every container
spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD') or 'start-singleuser.sh'
c.DockerSpawner.extra_create_kwargs.update({'command': spawn_cmd})

# Tell the user containers to connect to our docker network
network_name = os.environ.get('DOCKER_NETWORK_NAME') or 'jupyter-network'
c.DockerSpawner.network_name = network_name

# Remove containers when stopping the hub
c.DockerSpawner.remove_containers = True
c.DockerSpawner.remove = True

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
    f'{mnt_root}/{org_name}' + '/home/{raw_username}': notebook_dir,
    f'{mnt_root}/{org_name}/exchange': exchange_dir,
}

# add the shared folder if it was required
shared_folder_enabled = os.environ.get('SHARED_FOLDER_ENABLED') or 'False'
if shared_folder_enabled.lower() in ('true', '1'):
    c.DockerSpawner.volumes[f'{mnt_root}/{org_name}' + '/shared/'] = notebook_dir + '/shared'
c.DockerSpawner.name_template = 'jupyter-{raw_username}'

# start the container with root so we can update uid/gid using the docker-stacks hooks
c.DockerSpawner.extra_create_kwargs = {'user': '0'}

# these env vars are set within the docker image but add them here for good measure
c.DockerSpawner.environment = {'NB_UID': '1000', 'NB_GID': '100', 'NB_USER': 'jovyan'}

##########################################
# END CUSTOM DOCKERSPAWNER
##########################################
