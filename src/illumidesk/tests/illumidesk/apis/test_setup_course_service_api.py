import pytest
import os

from unittest.mock import patch

from illumidesk.apis.setup_course_service_api import SetupCourseServiceAPI


def test_initializer_sets_http_client(setup_course_hook_environ):
    """
    Does initializer set a httpclient instance?
    """
    sut = SetupCourseServiceAPI()
    assert sut.client is not None
    assert sut.client != ''


def test_initializer_sets_service_name_from_env_var(setup_course_hook_environ):
    """
    Does initializer set service name correctly?
    """
    sut = SetupCourseServiceAPI()
    assert sut.setup_course_service_name == os.environ.get('SETUP_COURSE_SERVICE_NAME')


def test_initializer_sets_service_port_from_env_var(setup_course_hook_environ):
    """
    Does initializer set the service port correctly?
    """
    sut = SetupCourseServiceAPI()
    assert sut.setup_course_port == os.environ.get('SETUP_COURSE_PORT')


def test_initializer_sets_headers_to_make_request(setup_course_hook_environ):
    """
    Does initializer set the api url?
    """
    sut = SetupCourseServiceAPI()
    assert sut.default_headers is not None
    assert type(sut.default_headers) is dict
    assert sut.default_headers['Content-Type'] == 'application/json'


@pytest.mark.asyncio
@patch('illumidesk.apis.setup_course_service_api.SetupCourseServiceAPI._request')
async def test_create_assignment_source_dir_request_helper_method_with_correct_values(
    mock_request, setup_course_hook_environ
):
    """
    Does create_assignment_source_dir method use the helper method and pass the correct values?
    """
    sut = SetupCourseServiceAPI()
    await sut.create_assignment_source_dir('some-org', 'some-course', 'some-assignment')
    assert mock_request.called
    mock_request.assert_called_with('/some-org/some-course/some-assignment', body='', method='GET')


@pytest.mark.asyncio
async def test_request_raises_value_error_with_endpoint_empty(setup_course_hook_environ):
    """
    Does the _request method accept an missing endpoint argument?
    """
    with pytest.raises(ValueError):
        await SetupCourseServiceAPI()._request(endpoint='')


def test_request_builds_correct_url_variable(setup_course_hook_environ):
    """
    Does the _request build the correct url based on the api url attribute and the endpoint argument?
    """
    endpoint = 'services'
    api_root_url = 'http://localhost:8000'
    actual = f'{api_root_url}/{endpoint}'
    expected = 'http://localhost:8000/services'
    assert expected == actual
