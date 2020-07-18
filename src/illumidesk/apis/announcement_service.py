import os


ANNOUNCEMENT_PORT = os.environ.get('ANNOUNCEMENT_SERVICE_PORT') or '8889'
jhub_base_url = os.environ.get('JUPYTERHUB_BASE_URL') or ''
ANNOUNCEMENT_PREFIX = f'{jhub_base_url}/services/announcement'

ANNOUNCEMENT_INTERNAL_URL = f'http://localhost:{int(ANNOUNCEMENT_PORT)}{ANNOUNCEMENT_PREFIX}'