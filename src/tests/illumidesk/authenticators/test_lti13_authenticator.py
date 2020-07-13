import pytest

from tornado.web import RequestHandler

from unittest.mock import patch

from illumidesk.authenticators.validator import LTI13LaunchValidator
from illumidesk.authenticators.authenticator import LTI13Authenticator

from tests.illumidesk.mocks import mock_handler
from tests.illumidesk.factory import dummy_lti13_id_token_complete
from tests.illumidesk.factory import dummy_lti13_id_token_empty_roles
from tests.illumidesk.factory import dummy_lti13_id_token_empty_workspace_type
from tests.illumidesk.factory import dummy_lti13_id_token_instructor_role
from tests.illumidesk.factory import dummy_lti13_id_token_learner_role
from tests.illumidesk.factory import dummy_lti13_id_token_student_role
from tests.illumidesk.factory import dummy_lti13_id_token_notebook_workspace_type
from tests.illumidesk.factory import dummy_lti13_id_token_rstudio_workspace_type
from tests.illumidesk.factory import dummy_lti13_id_token_theia_workspace_type
from tests.illumidesk.factory import dummy_lti13_id_token_vscode_workspace_type
from tests.illumidesk.factory import dummy_lti13_id_token_uncrecognized_workspace_type
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_email
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_name
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_given_name
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_family_name
from tests.illumidesk.factory import dummy_lti13_id_token_misssing_all_except_person_sourcedid


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_handler_get_argument():
    """
    Does the authenticator invoke the RequestHandler get_argument method?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        request_handler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()
    ) as mock_get_argument:
        _ = await authenticator.authenticate(request_handler, None)
        assert mock_get_argument.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_jwt_verify_and_decode(make_lti13_resource_link_request):
    """
    Does the authenticator invoke the LTI13Validator jwt_verify_and_decode method?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()):
        with patch.object(
            LTI13LaunchValidator, 'jwt_verify_and_decode', return_value=make_lti13_resource_link_request()
        ) as mock_verify_and_decode:
            _ = await authenticator.authenticate(request_handler, None)
            assert mock_verify_and_decode.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_validate_launch_request():
    """
    Does the authenticator invoke the LTI13Validator validate_launch_request method?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()):
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_authentication_request:
            _ = await authenticator.authenticate(request_handler, None)
            assert mock_verify_authentication_request.called


@pytest.mark.asyncio
async def test_authenticator_returns_course_id_in_auth_state_with_valid_resource_link_request(
    monkeypatch, auth_state_dict
):
    """
    Do we get a valid course_id when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            monkeypatch.setitem(auth_state_dict, 'name', 'foo')

            assert result['name'] == auth_state_dict['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_valid_email(monkeypatch, auth_state_dict):
    """
    Do we get a valid username when only including an email to the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_email.encode()
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            monkeypatch.setitem(auth_state_dict, 'name', 'foo')

            assert result['name'] == auth_state_dict['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_with_name(monkeypatch, auth_state_dict):
    """
    Do we get a valid username when only including the name in the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_name.encode()
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            monkeypatch.setitem(auth_state_dict, 'name', 'foo')

            assert result['name'] == auth_state_dict['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_with_given_name(monkeypatch, auth_state_dict):
    """
    Do we get a valid username when only including the given name in the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_given_name.encode()
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            monkeypatch.setitem(auth_state_dict, 'name', 'foobar')

            assert result['name'] == auth_state_dict['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_family_name(monkeypatch, auth_state_dict):
    """
    Do we get a valid username when only including the family name in the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_family_name.encode()
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            monkeypatch.setitem(auth_state_dict, 'name', 'bar')

            assert result['name'] == auth_state_dict['name']


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_person_sourcedid(monkeypatch, auth_state_dict):
    """
    Do we get a valid username when only including lis person sourcedid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_misssing_all_except_person_sourcedid.encode()
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            monkeypatch.setitem(auth_state_dict, 'name', 'abc123')

            assert result['name'] == auth_state_dict['name']


@pytest.mark.asyncio
async def test_authenticator_returns_workspace_type_in_auth_state(monkeypatch, auth_state_dict):
    """
    Do we get a valid lms_user_id in the auth_state when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_complete.encode()):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            monkeypatch.setitem(auth_state_dict, 'lms_user_id', '8171934b-f5e2-4f4e-bdbd-6d798615b93e')

            assert result['auth_state'].get('lms_user_id') == auth_state_dict.get('lms_user_id')


@pytest.mark.asyncio
async def test_authenticator_returns_learner_role_in_auth_state(monkeypatch, auth_state_dict):
    """
    Do we set the learner role in the auth_state when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'user_role', 'Learner')
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_learner_role.encode()):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == auth_state_dict['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_instructor_role_in_auth_state_with_instructor_role(monkeypatch, auth_state_dict):
    """
    Do we set the instructor role in the auth_state when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'user_role', 'Instructor')
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_instructor_role.encode()):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == auth_state_dict['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_student_role_in_auth_state_with_learner_role(monkeypatch, auth_state_dict):
    """
    Do we set the student role in the auth_state when receiving a valid resource link request with the Learner role?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'user_role', 'Learner')
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_learner_role.encode()):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == auth_state_dict['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_student_role_in_auth_state_with_student_role(monkeypatch, auth_state_dict):
    """
    Do we set the student role in the auth_state when receiving a valid resource link request with the Student role?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'user_role', 'Learner')
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_student_role.encode()):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == auth_state_dict['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_learner_role_in_auth_state_with_empty_roles(monkeypatch, auth_state_dict):
    """
    Do we set the learner role in the auth_state when receiving resource link request
    with empty roles?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'notebook')
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_empty_roles.encode()):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == auth_state_dict['auth_state']['user_role']


@pytest.mark.asyncio
async def test_authenticator_returns_standard_workspace_image_with_unrecognized_workspace_type_in_auth_state(
    monkeypatch, auth_state_dict
):
    """
    Do we set the default notebook image when the workspace type is unrecognized?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'notebook')
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_uncrecognized_workspace_type.encode()
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == auth_state_dict['auth_state']['workspace_type']


@pytest.mark.asyncio
async def test_authenticator_returns_standard_workspace_image_with_missing_workspace_type_in_auth_state(
    monkeypatch, auth_state_dict
):
    """
    Do we set the default notebook image when the workspace type is missing?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'notebook')
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_empty_workspace_type.encode()):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == auth_state_dict['auth_state']['workspace_type']


@pytest.mark.asyncio
async def test_authenticator_returns_notebook_workspace_image_with_notebook_workspace_type_in_auth_state(
    monkeypatch, auth_state_dict
):
    """
    Do we set the workspace image to the notebook image when setting the workspace type to notebook?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'notebook')
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_notebook_workspace_type.encode()
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == auth_state_dict['auth_state']['workspace_type']


@pytest.mark.asyncio
async def test_authenticator_returns_rstudio_workspace_image_with_rstudio_workspace_type_in_auth_state(
    monkeypatch, auth_state_dict
):
    """
    Do we set the workspace image to the rstudio image when setting the workspace type to rstudio?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'rstudio')
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_rstudio_workspace_type.encode()
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == auth_state_dict['auth_state']['workspace_type']


@pytest.mark.asyncio
async def test_authenticator_returns_theia_workspace_image_with_theia_workspace_type_in_auth_state(
    monkeypatch, auth_state_dict
):
    """
    Do we set the workspace image to the theia image when setting the workspace type to tbeia?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'theia')
    with patch.object(RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_theia_workspace_type.encode()):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == auth_state_dict['auth_state']['workspace_type']


@pytest.mark.asyncio
async def test_authenticator_returns_vscode_workspace_image_with_vscode_workspace_type_in_auth_state(
    monkeypatch, auth_state_dict
):
    """
    Do we set the workspace image to the vscode image when setting the workspace type to vscode?
    """
    authenticator = LTI13Authenticator()
    request_handler = mock_handler(RequestHandler, authenticator=authenticator)
    monkeypatch.setitem(auth_state_dict['auth_state'], 'workspace_type', 'vscode')
    with patch.object(
        RequestHandler, 'get_argument', return_value=dummy_lti13_id_token_vscode_workspace_type.encode()
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == auth_state_dict['auth_state']['workspace_type']
