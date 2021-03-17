import pytest
import os

from unittest.mock import patch

from illumidesk.apis.setup_course_service_api import SetupCourseServiceAPI


def test_initializer_sets_service_name_from_env_var(setup_course_hook_environ):
    """
    Does initializer set service name correctly?
    """
    sut = SetupCourseServiceAPI()
    assert sut.setup_course_service_name == os.environ.get('SETUP_COURSE_SERVICE_NAME')


@pytest.mark.asyncio
async def test_initializer_sets_setup_course_service_name_if_empty(monkeypatch, setup_course_hook_environ):
    """
    Does the initializer for the SetupCourseServiceAPI method set the setup_course_service_name attribute if missing?
    """
    sut = SetupCourseServiceAPI()
    monkeypatch.setenv('SETUP_COURSE_SERVICE_NAME', '')
    sut.setup_course_service_name = 'grader-setup-service'


@pytest.mark.asyncio
async def test_initializer_sets_setup_course_service_port_if_empty(monkeypatch, setup_course_hook_environ):
    """
    Does the initializer for the SetupCourseServiceAPI method set the setup_course_service_port attribute if missing?
    """
    sut = SetupCourseServiceAPI()
    monkeypatch.setenv('SETUP_COURSE_SERVICE_PORT', '')
    sut.setup_course_service_name = '8000'


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
    assert mock_request.await_args('/some-org/some-course/some-assignment', body='', method='GET')


@pytest.mark.asyncio
@patch('illumidesk.apis.setup_course_service_api.SetupCourseServiceAPI._request')
async def test_create_assignment_source_dir_raise_http_error_for_response_not_200(
    mock_request, setup_course_hook_environ
):
    """
    Does create_assignment_source_dir method use the helper method and pass the correct values?
    """
    with patch.object(
        SetupCourseServiceAPI, 'create_assignment_source_dir', side_effect=Exception('mocked error')
    ) as mock_function:
        with pytest.raises(Exception) as excinfo:
            assert excinfo.value.message == 'mocked error'
            assert not mock_function.return_value


@pytest.mark.asyncio
@patch('illumidesk.apis.setup_course_service_api.SetupCourseServiceAPI._request')
async def test_register_new_service_raise_http_error_for_response_not_200(mock_request, setup_course_hook_environ):
    """
    Does register_new_service method use the helper method and pass the correct values?
    """
    with patch.object(
        SetupCourseServiceAPI, 'register_new_service', side_effect=Exception('mocked error')
    ) as mock_function:
        with pytest.raises(Exception) as excinfo:
            assert excinfo.value.message == 'mocked error'
            assert not mock_function.return_value


@pytest.mark.asyncio
@patch('illumidesk.apis.setup_course_service_api.SetupCourseServiceAPI._request')
async def test_register_control_file_raise_http_error_for_response_not_200(mock_request, setup_course_hook_environ):
    """
    Does register_control_file method use the helper method and pass the correct values?
    """
    with patch.object(
        SetupCourseServiceAPI, 'register_control_file', side_effect=Exception('mocked error')
    ) as mock_function:
        with pytest.raises(Exception) as excinfo:
            assert excinfo.value.message == 'mocked error'
            assert not mock_function.return_value


@pytest.mark.asyncio
@patch('illumidesk.apis.setup_course_service_api.SetupCourseServiceAPI._request')
async def test_register_new_service_request_helper_method_with_correct_values(mock_request, setup_course_hook_environ):
    """
    Does register_new_service method use the helper method and pass the correct values?
    """
    sut = SetupCourseServiceAPI()
    await sut.register_new_service('some-org', 'some-course')
    assert mock_request.called
    assert mock_request.await_args('/some-org/some-course', body='', method='GET')


@pytest.mark.asyncio
@patch('illumidesk.apis.setup_course_service_api.SetupCourseServiceAPI._request')
async def test_register_control_file_request_helper_method_with_correct_values(
    mock_request, setup_course_hook_environ
):
    """
    Does register_control_file method use the helper method and pass the correct values?
    """
    sut = SetupCourseServiceAPI()
    await sut.register_control_file('some-assignment', 'some-outcome', 'some-sourceid', 'some-lms', 'some-course')
    assert mock_request.called
    assert mock_request.await_args(
        '/some-assignment/some-outcome/some-sourceid/some-lms/some-course', body='', method='GET'
    )


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
