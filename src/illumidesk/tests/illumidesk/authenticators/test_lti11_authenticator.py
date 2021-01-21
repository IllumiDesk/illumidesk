import pytest
import json

from tornado.web import RequestHandler
from tornado.httputil import HTTPServerRequest

from unittest.mock import Mock
from unittest.mock import patch

from illumidesk.authenticators.validator import LTI11LaunchValidator
from illumidesk.authenticators.authenticator import LTI11Authenticator
from illumidesk.authenticators.authenticator import LTIUtils
from illumidesk.grades.senders import LTIGradesSenderControlFile


@pytest.fixture(scope='function')
def gradesender_controlfile_mock():
    with patch.multiple(
        'illumidesk.grades.sender_controlfile.LTIGradesSenderControlFile',
        _loadFromFile=Mock(),
        register_data=Mock(return_value=None),
    ) as mock_controlfile:
        with patch('pathlib.Path.mkdir'):
            yield mock_controlfile


@pytest.mark.asyncio
@patch('illumidesk.authenticators.validator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_canvas_fields(
    mock_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Do we get a valid username when sending an argument with the custom canvas id?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=make_lti11_success_authentication_request_args('canvas'),
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1-1091',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.validator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_other_lms_vendor(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Do we get a valid username with lms vendors other than canvas?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=make_lti11_success_authentication_request_args('moodle'),
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
async def test_authenticator_uses_lti11validator(
    make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Ensure that we call the LTI11Validator from the LTI11Authenticator.
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True) as mock_validator:

        authenticator = LTI11Authenticator()
        handler = Mock(spec=RequestHandler)
        request = HTTPServerRequest(
            method='POST',
            connection=Mock(),
        )
        handler.request = request

        handler.request.arguments = make_lti11_success_authentication_request_args('lmsvendor')
        handler.request.get_argument = lambda x, strip=True: make_lti11_success_authentication_request_args(
            'lmsvendor'
        )[x][0].decode()

        _ = await authenticator.authenticate(handler, None)
        assert mock_validator.called


@pytest.mark.asyncio
async def test_authenticator_uses_lti_utils_normalize_string(
    make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Ensure that we call the normalize string method with the LTI11Authenticator.
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        with patch.object(LTIUtils, 'normalize_string', return_value='foobar') as mock_normalize_string:
            authenticator = LTI11Authenticator()
            handler = Mock(spec=RequestHandler)
            request = HTTPServerRequest(
                method='POST',
                connection=Mock(),
            )
            handler.request = request

            handler.request.arguments = make_lti11_success_authentication_request_args('lmsvendor')
            handler.request.get_argument = lambda x, strip=True: make_lti11_success_authentication_request_args(
                'lmsvendor'
            )[x][0].decode()

            _ = await authenticator.authenticate(handler, None)
            assert mock_normalize_string.called


@pytest.mark.asyncio
@patch('pathlib.Path.mkdir')
async def test_authenticator_uses_lti_grades_sender_control_file_with_student_role(
    mock_mkdir, tmp_path, make_lti11_success_authentication_request_args, mock_nbhelper
):
    """
    Is the LTIGradesSenderControlFile class register_data method called when setting the user_role with the
    Student string?
    """

    def _change_flag():
        LTIGradesSenderControlFile.FILE_LOADED = True

    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        with patch.object(LTIGradesSenderControlFile, 'register_data', return_value=None) as mock_register_data:
            with patch.object(
                LTIGradesSenderControlFile, '_loadFromFile', return_value=None
            ) as mock_loadFromFileMethod:
                mock_loadFromFileMethod.side_effect = _change_flag
                authenticator = LTI11Authenticator()
                handler = Mock(spec=RequestHandler)
                request = HTTPServerRequest(
                    method='POST',
                    connection=Mock(),
                )
                handler.request = request
                handler.request.arguments = make_lti11_success_authentication_request_args(
                    lms_vendor='edx', role='Student'
                )
                handler.request.get_argument = lambda x, strip=True: make_lti11_success_authentication_request_args(
                    'Student'
                )[x][0].decode()

                _ = await authenticator.authenticate(handler, None)
                assert mock_register_data.called


@pytest.mark.asyncio
@patch('pathlib.Path.mkdir')
async def test_authenticator_uses_lti_grades_sender_control_file_with_learner_role(
    mock_mkdir, tmp_path, make_lti11_success_authentication_request_args, mock_nbhelper
):
    """
    Is the LTIGradesSenderControlFile class register_data method called when setting the user_role with the
    Learner string?
    """

    def _change_flag():
        LTIGradesSenderControlFile.FILE_LOADED = True

    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        with patch.object(LTIGradesSenderControlFile, 'register_data', return_value=None) as mock_register_data:
            with patch.object(
                LTIGradesSenderControlFile, '_loadFromFile', return_value=None
            ) as mock_loadFromFileMethod:
                mock_loadFromFileMethod.side_effect = _change_flag
                authenticator = LTI11Authenticator()
                handler = Mock(spec=RequestHandler)
                request = HTTPServerRequest(
                    method='POST',
                    connection=Mock(),
                )
                handler.request = request
                handler.request.arguments = make_lti11_success_authentication_request_args(
                    lms_vendor='canvas', role='Learner'
                )
                handler.request.get_argument = lambda x, strip=True: make_lti11_success_authentication_request_args(
                    'Learner'
                )[x][0].decode()

                _ = await authenticator.authenticate(handler, None)
                assert mock_register_data.called


@pytest.mark.asyncio
@patch('pathlib.Path.mkdir')
async def test_authenticator_uses_lti_grades_sender_control_file_with_instructor_role(
    mock_mkdir, tmp_path, make_lti11_success_authentication_request_args, mock_nbhelper
):
    """
    Is the LTIGradesSenderControlFile class register_data method called when setting the user_role with the
    Instructor string?
    """

    def _change_flag():
        LTIGradesSenderControlFile.FILE_LOADED = True

    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        with patch.object(LTIGradesSenderControlFile, 'register_data', return_value=None) as mock_register_data:
            with patch.object(
                LTIGradesSenderControlFile, '_loadFromFile', return_value=None
            ) as mock_loadFromFileMethod:
                mock_loadFromFileMethod.side_effect = _change_flag
                authenticator = LTI11Authenticator()
                handler = Mock(spec=RequestHandler)
                request = HTTPServerRequest(
                    method='POST',
                    connection=Mock(),
                )
                handler.request = request
                handler.request.arguments = make_lti11_success_authentication_request_args(
                    lms_vendor='canvas', role='Instructor'
                )
                handler.request.get_argument = lambda x, strip=True: make_lti11_success_authentication_request_args(
                    'Instructor'
                )[x][0].decode()

                _ = await authenticator.authenticate(handler, None)
                assert mock_register_data.called


@pytest.mark.asyncio
async def test_authenticator_invokes_validator_with_decoded_dict(
    make_lti11_success_authentication_request_args, mock_nbhelper, gradesender_controlfile_mock
):
    """
    Does the authentictor call the validator?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True) as mock_validator:
        authenticator = LTI11Authenticator()
        handler = Mock(spec=RequestHandler)
        request = HTTPServerRequest(method='POST', uri='/hub', host='example.com')
        handler.request = request
        handler.request.protocol = 'https'
        handler.request.arguments = make_lti11_success_authentication_request_args('canvas')
        handler.request.get_argument = lambda x, strip=True: make_lti11_success_authentication_request_args('canvas')[
            x
        ][0].decode()

        _ = await authenticator.authenticate(handler, None)
        # check our validator was called
        assert mock_validator.called
        decoded_args = {
            k: handler.request.get_argument(k, strip=False)
            for k, v in make_lti11_success_authentication_request_args('canvas').items()
        }
        # check validator was called with correct dict params (decoded)
        mock_validator.assert_called_with('https://example.com/hub', {}, decoded_args)


@pytest.mark.asyncio
@patch('illumidesk.authenticators.validator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_missing_lis_outcome_service_url(
    lti11_validator, make_lti11_success_authentication_request_args, mock_nbhelper, gradesender_controlfile_mock
):
    """
    Are we able to handle requests with a missing lis_outcome_service_url key?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('canvas', 'Learner')
        del args['lis_outcome_service_url']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1-1091',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Learner',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.validator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_missing_lis_result_sourcedid(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Are we able to handle requests with a missing lis_result_sourcedid key?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('canvas', 'Learner')
        del args['lis_result_sourcedid']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1-1091',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Learner',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_empty_lis_result_sourcedid(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Are we able to handle requests with lis_result_sourcedid set to an empty value?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('canvas', 'Learner')
        args['lis_result_sourcedid'] = [b'']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1-1091',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Learner',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_auth_state_with_empty_lis_outcome_service_url(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Are we able to handle requests with lis_outcome_service_url set to an empty value?
    """
    with patch.object(LTI11LaunchValidator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('canvas', 'Learner')
        args['lis_outcome_service_url'] = [b'']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'student1-1091',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Learner',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_correct_username_when_using_email_as_username(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Do we get a valid username when the username is sent as the primary email address?
    """
    with patch.object(lti11_validator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('edx', 'Instructor')
        args['custom_canvas_user_login_id'] = [b'']
        args['lis_person_contact_email_primary'] = [b'foo@example.com']
        args['lis_person_name_family'] = [b'']
        args['lis_person_name_full'] = [b'']
        args['lis_person_name_given'] = [b'']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_correct_course_id_when_using_context_label_given_as_course_name(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Do we get a valid course name when the request includes a context_label?
    """
    with patch.object(lti11_validator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('d2l', 'Instructor')
        args['lis_person_contact_email_primary'] = [b'foo@example.com']
        args['context_label'] = [b'intro101']
        args['context_title'] = [b'']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_correct_course_id_when_using_context_title_given_as_course_name(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Do we get a valid course name when the request includes a context_title?
    """
    with patch.object(lti11_validator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('d2l', 'Instructor')
        args['lis_person_contact_email_primary'] = [b'foo@example.com']
        args['context_label'] = [b'']
        args['context_title'] = [b'intro101']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_correct_username_when_using_lis_person_name_given_as_username(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Do we get a valid username when the username is sent as the primary email address?
    """
    with patch.object(lti11_validator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('d2l', 'Instructor')
        args['custom_canvas_user_login_id'] = [b'']
        args['lis_person_contact_email_primary'] = [b'']
        args['lis_person_name_given'] = [b'foo']
        args['lis_person_name_family'] = [b'']
        args['lis_person_name_full'] = [b'']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foo',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_correct_username_when_using_lis_person_name_family_as_username(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Do we get a valid username when the username is sent with the family name?
    """
    with patch.object(lti11_validator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('edx', 'Instructor')
        args['custom_canvas_user_login_id'] = [b'']
        args['lis_person_contact_email_primary'] = [b'']
        args['lis_person_name_given'] = [b'']
        args['lis_person_name_family'] = [b'Bar']
        args['lis_person_name_full'] = [b'']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'bar',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_correct_username_when_using_lis_person_name_full_as_username(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Do we get a valid username when the username is sent with the family name?
    """
    with patch.object(lti11_validator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('moodle', 'Instructor')
        args['custom_canvas_user_login_id'] = [b'']
        args['lis_person_contact_email_primary'] = [b'']
        args['lis_person_name_given'] = [b'']
        args['lis_person_name_family'] = [b'']
        args['lis_person_name_full'] = [b'Foo Bar']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foobar',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_username_from_user_id_with_another_lms(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Ensure the username doesn't exceed thirty characters when using the user_id as username.
    """
    with patch.object(lti11_validator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('moodle', 'Instructor')
        args['custom_canvas_user_login_id'] = [b'']
        args['lis_person_contact_email_primary'] = [b'']
        args['lis_person_name_given'] = [b'']
        args['lis_person_name_family'] = [b'']
        args['lis_person_name_full'] = [b'']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': '185d6c59731a553009ca9b59c',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected


@pytest.mark.asyncio
@patch('illumidesk.authenticators.authenticator.LTI11LaunchValidator')
async def test_authenticator_returns_login_id_plus_user_id_as_username_with_canvas(
    lti11_validator, make_lti11_success_authentication_request_args, gradesender_controlfile_mock, mock_nbhelper
):
    """
    Ensure the username reflects the custom_canvas_user_login_id and custom_canvas_user_id
    when the lms vendor is canvas.
    """
    with patch.object(lti11_validator, 'validate_launch_request', return_value=True):
        authenticator = LTI11Authenticator()
        args = make_lti11_success_authentication_request_args('canvas', 'Instructor')
        args['custom_canvas_user_login_id'] = [b'foobar']
        args['custom_canvas_user_id'] = [b'123123']
        args['lis_person_contact_email_primary'] = [b'']
        args['lis_person_name_given'] = [b'']
        args['lis_person_name_family'] = [b'']
        args['lis_person_name_full'] = [b'']
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(['key', 'secret'])),
            request=Mock(
                arguments=args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            'name': 'foobar-123123',
            'auth_state': {
                'course_id': 'intro101',
                'lms_user_id': '185d6c59731a553009ca9b59ca3a885100000',
                'user_role': 'Instructor',
            },
        }
        assert result == expected
