import json
import os
import pytest

from illumidesk.apis.announcement_service import ANNOUNCEMENT_INTERNAL_URL, AnnouncementService

from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler

from unittest.mock import patch


@pytest.mark.asyncio
async def test_add_announcement_method_calls_announcement_service(
    jupyterhub_api_environ, make_http_response, make_mock_request_handler
):
    local_handler = make_mock_request_handler(RequestHandler)
    sut = AnnouncementService
    headers = {'Content-Type': 'application/json', 'Authorization': f'token {os.environ.get("JUPYTERHUB_API_TOKEN")}'}
    with patch.object(
        AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request)
    ) as mock_client:
        await sut.add_announcement('A new service was detected, please reload this page...')
        # the announcement service was called by using specific args
        mock_client.assert_any_call(
            ANNOUNCEMENT_INTERNAL_URL,
            headers=headers,
            body=json.dumps({'announcement': 'A new service was detected, please reload this page...'}),
            method='POST',
        )
