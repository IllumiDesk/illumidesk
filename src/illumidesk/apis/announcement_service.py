import json
import os
from tornado.httpclient import AsyncHTTPClient

jhub_base_url = os.environ.get('JUPYTERHUB_BASE_URL') or ''
# Constants
ANNOUNCEMENT_PORT = os.environ.get('ANNOUNCEMENT_SERVICE_PORT') or '8889'
ANNOUNCEMENT_PREFIX = f'{jhub_base_url}/services/announcement'

ANNOUNCEMENT_INTERNAL_URL = f'http://localhost:{int(ANNOUNCEMENT_PORT)}{ANNOUNCEMENT_PREFIX}'

ANNOUNCEMENT_JHUB_SERVICE_DEFINITION = {
    'name': 'announcement',
    'url': f'http://0.0.0.0:{int(ANNOUNCEMENT_PORT)}',  # allow external connections with 0.0.0.0
    'command': f'python3 /srv/jupyterhub/announcement.py --port {int(ANNOUNCEMENT_PORT)} --api-prefix {ANNOUNCEMENT_PREFIX}'.split(),
}


class AnnouncementService:
    """
    Class helper to add announcements using a jupyterhub internal service (normally located at services/announcement)
    """

    @staticmethod
    async def add_announcement(message: str) -> None:
        # It should not raise an error if a message is not passed
        if not message:
            return
        # we need to call jhub services with Authorization header
        jupyterhub_api_token = os.environ.get('JUPYTERHUB_API_TOKEN')

        headers = {'Content-Type': 'application/json'}
        headers['Authorization'] = f'token {jupyterhub_api_token}'
        body_data = {'announcement': message}
        client = AsyncHTTPClient()
        await client.fetch(ANNOUNCEMENT_INTERNAL_URL, headers=headers, body=json.dumps(body_data), method='POST')
