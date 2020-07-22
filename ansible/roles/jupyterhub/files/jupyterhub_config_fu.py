import os

from dockerspawner import DockerSpawner  # noqa: F401

from illumidesk.spawners.spawners import IllumiDeskWorkSpaceDockerSpawner


c = get_config()

# FIRST load the base configuration file (with common settings)
load_subconfig('/etc/jupyterhub/jupyterhub_config_base.py')
# THEN override the settings that apply only with LT13 authentication type

# The instructor1 and instructor2 users have access to different shared
# grader notebooks. bitdiddle, hacker, and reasoner students are from
# the `nbgrader quickstart <course name>` command.
course_id = os.environ.get('COURSE_ID')
c.JupyterHub.load_groups = {
    os.environ.get('DEMO_INSTRUCTOR_GROUP')
    or f'formgrade-{course_id}': [
        'instructor1',
        'instructor2',
        os.environ.get('DEMO_GRADER_NAME') or f'grader-{course_id}',
    ],  # noqa: E231
    os.environ.get('DEMO_STUDENT_GROUP')
    or f'nbgrader-{course_id}': ['student1', 'bitdiddle', 'hacker', 'reasoner',],  # noqa: E231
}

# Start the grader notebook as a service. The port can be whatever you want
# and the group has to match the name of the DEMO_GRADER_NAME group defined above.
# The cull_idle service conserves resources.
c.JupyterHub.services.append(
    {
        'name': course_id,
        'url': f'http://{course_id}:8888',
        'oauth_no_confirm': True,
        'admin': True,
        'api_token': os.environ.get('JUPYTERHUB_API_TOKEN'),
    }
)

# User authentication class
c.JupyterHub.authenticator_class = 'firstuseauthenticator.FirstUseAuthenticator'
# Spawn containers with custom dockerspawner class
c.JupyterHub.spawner_class = IllumiDeskWorkSpaceDockerSpawner
##########################################
# END JUPYTERHUB APPLICATION
##########################################

##########################################
# BEGIN FIRSTUSE AUTHENTICATION
##########################################
# Our user list for demos when using FirstUseAuthenticator. Uncomment and add initial
# users as needed. This avoids having the login form which accepts any username/password
c.Authenticator.whitelist = [
    'admin',
    'instructor1',
    'instructor2',
    'student1',
    'bitdiddle',
    'hacker',
    'reasoner',
    os.environ.get('DEMO_GRADER_NAME'),
]
# Refrain from creating users within the JupyterHub container
# c.FirstUseAuthenticator.create_users = False

##########################################
# END FIRSTUSE AUTHENTICATION
##########################################
