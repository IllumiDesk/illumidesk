import pytest

from unittest.mock import patch

from tornado.httputil import HTTPHeaders

from illumidesk.grades.senders import LTIGradeSender
from illumidesk.grades.senders import LTI13GradeSender
from illumidesk.grades.exceptions import AssignmentWithoutGradesError
from illumidesk.grades.exceptions import GradesSenderMissingInfoError
from illumidesk.grades.sender_controlfile import LTIGradesSenderControlFile

from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler


class TestLTI11GradesSender:
    @pytest.mark.asyncio
    async def test_grades_sender_raises_an_error_if_there_are_no_grades(self, tmp_path):
        """
        Does the sender raise an error when there are no grades?
        """
        sender_controlfile = LTIGradeSender('course1', 'problem1')
        # create a mock for our method that searches grades from gradebook.db
        with patch.object(LTIGradeSender, '_retrieve_grades_from_db', return_value=(lambda: 10, [])):
            with pytest.raises(AssignmentWithoutGradesError):
                await sender_controlfile.send_grades()

    @pytest.mark.asyncio
    async def test_grades_sender_raises_an_error_if_assignment_not_found_in_control_file(self, tmp_path):
        """
        Does the sender raise an error when there are grades but control file does not contain info related with
        the gradebook data?
        """
        sender_controlfile = LTIGradeSender('course1', 'problem1')
        _ = LTIGradesSenderControlFile(tmp_path)
        grades_nbgrader = [{'score': 10, 'lms_user_id': 'user1'}]
        # create a mock for our method that searches grades from gradebook.db
        with patch.object(LTIGradeSender, '_retrieve_grades_from_db', return_value=(lambda: 10, grades_nbgrader)):
            with pytest.raises(GradesSenderMissingInfoError):
                await sender_controlfile.send_grades()


class TestLTI13GradesSender:
    def test_sender_sets_lineitems_url_with_the_value_in_auth_state_dict(self, lti13_config_environ, mock_nbhelper):
        sut = LTI13GradeSender('course-id', 'lab')
        assert sut.course.lms_lineitems_endpoint == 'canvas.docker.com/api/lti/courses/1/line_items'

    @pytest.mark.asyncio
    async def test_sender_raises_AssignmentWithoutGradesError_if_there_are_no_grades(
        self, lti13_config_environ, mock_nbhelper
    ):
        sut = LTI13GradeSender('course-id', 'lab')
        with patch.object(LTI13GradeSender, '_retrieve_grades_from_db', return_value=(lambda: 10, [])):
            with pytest.raises(AssignmentWithoutGradesError):
                await sut.send_grades()

    @pytest.mark.asyncio
    async def test_sender_calls_set_access_token_header_before_to_send_grades(
        self, lti13_config_environ, make_http_response, make_mock_request_handler, mock_nbhelper
    ):
        sut = LTI13GradeSender('course-id', 'lab')
        local_handler = make_mock_request_handler(RequestHandler)
        access_token_result = {'token_type': '', 'access_token': ''}
        line_item_result = {'label': 'lab', 'id': 'line_item_url', 'scoreMaximum': 40}
        with patch('illumidesk.grades.senders.get_lms_access_token', return_value=access_token_result) as mock_method:
            with patch.object(
                LTI13GradeSender,
                '_retrieve_grades_from_db',
                return_value=(lambda: 10, [{'score': 10, 'lms_user_id': 'id'}]),
            ):

                with patch.object(
                    AsyncHTTPClient,
                    'fetch',
                    side_effect=[
                        make_http_response(handler=local_handler.request, body=[line_item_result]),
                        make_http_response(handler=local_handler.request, body=line_item_result),
                        make_http_response(handler=local_handler.request, body=[]),
                    ],
                ):
                    await sut.send_grades()
                    assert mock_method.called

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_async_httpclient_with_simple_response", [[]], indirect=True)
    async def test_sender_raises_an_error_if_no_line_items_were_found(
        self, lti13_config_environ, http_async_httpclient_with_simple_response, mock_nbhelper
    ):
        sut = LTI13GradeSender('course-id', 'lab')

        access_token_result = {'token_type': '', 'access_token': ''}
        with patch('illumidesk.grades.senders.get_lms_access_token', return_value=access_token_result):

            with patch.object(
                LTI13GradeSender, '_retrieve_grades_from_db', return_value=(lambda: 10, [{'score': 10}])
            ):
                with pytest.raises(GradesSenderMissingInfoError):
                    await sut.send_grades()

    @pytest.mark.asyncio
    async def test_get_lineitems_from_url_method_does_fetch_lineitems_from_url(
        self, lti13_config_environ, mock_nbhelper, make_http_response, make_mock_request_handler
    ):
        local_handler = make_mock_request_handler(RequestHandler)
        sut = LTI13GradeSender('course-id', 'lab')
        lineitems_url = 'https://example.canvas.com/api/lti/courses/111/line_items'
        with patch.object(
            AsyncHTTPClient, 'fetch', return_value=make_http_response(handler=local_handler.request)
        ) as mock_client:
            await sut._get_lineitems_from_url(lineitems_url)
            assert mock_client.called
            mock_client.assert_called_with(lineitems_url, method='GET', headers={})

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "http_async_httpclient_with_simple_response",
        [[{"id": "value", "scoreMaximum": 0.0, "label": "label", "resourceLinkId": "abc"}]],
        indirect=True,
    )
    async def test_get_lineitems_from_url_method_sets_all_lineitems_property(
        self, lti13_config_environ, mock_nbhelper, http_async_httpclient_with_simple_response
    ):
        sut = LTI13GradeSender('course-id', 'lab')

        await sut._get_lineitems_from_url('https://example.canvas.com/api/lti/courses/111/line_items')
        assert len(sut.all_lineitems) == 1

    @pytest.mark.asyncio
    async def test_get_lineitems_from_url_method_calls_itself_recursively(
        self, lti13_config_environ, mock_nbhelper, make_http_response, make_mock_request_handler
    ):
        local_handler = make_mock_request_handler(RequestHandler)
        sut = LTI13GradeSender('course-id', 'lab')

        lineitems_body_result = {
            'body': [{"id": "value", "scoreMaximum": 0.0, "label": "label", "resourceLinkId": "abc"}]
        }
        lineitems_body_result['headers'] = HTTPHeaders(
            {
                'content-type': 'application/vnd.ims.lis.v2.lineitemcontainer+json',
                'link': '<https://learning.flatironschool.com/api/lti/courses/691/line_items?page=2&per_page=10>; rel="next"',
            }
        )

        with patch.object(
            AsyncHTTPClient,
            'fetch',
            side_effect=[
                make_http_response(handler=local_handler.request, **lineitems_body_result),
                make_http_response(handler=local_handler.request, body=lineitems_body_result['body']),
            ],
        ) as mock_fetch:
            # initial call then the method will detect the Link header to get the next items
            await sut._get_lineitems_from_url('https://example.canvas.com/api/lti/courses/111/line_items')
            # assert the lineitems number
            assert len(sut.all_lineitems) == 2
            # assert the number of calls
            assert mock_fetch.call_count == 2
