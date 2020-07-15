import pytest

from unittest.mock import patch

from illumidesk.grades.senders import LTIGradeSender
from illumidesk.grades.senders import LTI13GradeSender
from illumidesk.grades.exceptions import GradesSenderCriticalError
from illumidesk.grades.exceptions import AssignmentWithoutGradesError
from illumidesk.grades.exceptions import GradesSenderMissingInfoError
from illumidesk.grades.sender_controlfile import LTIGradesSenderControlFile

from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler


class TestLTI11GradesSender:
    @pytest.mark.asyncio
    async def test_grades_sender_raises_a_critical_error_when_gradebook_does_not_exist(self, tmp_path):
        """
        Does the sender raises an error when the gradebook db is not found?
        """
        sender_controlfile = LTIGradeSender('course1', 'problem1')
        with pytest.raises(GradesSenderCriticalError):
            await sender_controlfile.send_grades()

    @pytest.mark.asyncio
    async def test_grades_sender_raises_an_error_if_there_are_no_grades(self, tmp_path):
        """
        Does the sender raises an error when there are no grades?
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
    def test_sender_raises_an_error_without_auth_state_information(self):
        with pytest.raises(GradesSenderMissingInfoError):
            LTI13GradeSender('course-id', 'lab', None)

    def test_sender_sets_lineitems_url_with_the_value_in_auth_state_dict(self, lti_config_environ):
        sut = LTI13GradeSender(
            'course-id', 'lab', {'course_lineitems': 'canvas.docker.com/api/lti/courses/1/line_items'}
        )
        assert sut.lineitems_url == 'canvas.docker.com/api/lti/courses/1/line_items'

    @pytest.mark.asyncio
    async def test_sender_raises_AssignmentWithoutGradesError_if_there_are_not_grades(self, lti_config_environ):
        sut = LTI13GradeSender(
            'course-id', 'lab', {'course_lineitems': 'canvas.docker.com/api/lti/courses/1/line_items'}
        )
        with patch.object(LTI13GradeSender, '_retrieve_grades_from_db', return_value=(lambda: 10, [])):
            with pytest.raises(AssignmentWithoutGradesError):
                await sut.send_grades()

    @pytest.mark.asyncio
    async def test_sender_calls__set_access_token_header_before_to_send_grades(
        self, lti_config_environ, make_http_response, make_mock_request_handler
    ):
        sut = LTI13GradeSender(
            'course-id', 'lab', {'course_lineitems': 'canvas.docker.com/api/lti/courses/1/line_items'}
        )
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
        self, lti_config_environ, http_async_httpclient_with_simple_response
    ):
        sut = LTI13GradeSender(
            'course-id', 'lab', {'course_lineitems': 'canvas.docker.com/api/lti/courses/1/line_items'}
        )

        access_token_result = {'token_type': '', 'access_token': ''}
        with patch('illumidesk.grades.senders.get_lms_access_token', return_value=access_token_result) as mock_method:

            with patch.object(
                LTI13GradeSender, '_retrieve_grades_from_db', return_value=(lambda: 10, [{'score': 10}])
            ):
                with pytest.raises(GradesSenderMissingInfoError):
                    await sut.send_grades()
