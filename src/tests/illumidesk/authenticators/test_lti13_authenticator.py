import pytest

from tornado.web import RequestHandler

from unittest.mock import patch

from illumidesk.authenticators.validator import LTI13LaunchValidator
from illumidesk.authenticators.authenticator import LTI13Authenticator
from illumidesk.authenticators.authenticator import LTIUtils


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_handler_get_argument(
    build_lti13_jwt_id_token, make_lti13_resource_link_request, make_mock_request_handler
):
    """
    Does the authenticator invoke the RequestHandler get_argument method?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        request_handler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ) as mock_get_argument:
        _ = await authenticator.authenticate(request_handler, None)
        assert mock_get_argument.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_jwt_verify_and_decode(
    make_lti13_resource_link_request, make_mock_request_handler
):
    """
    Does the authenticator invoke the LTI13Validator jwt_verify_and_decode method?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    with patch.object(RequestHandler, 'get_argument', return_value=None):
        with patch.object(
            LTI13LaunchValidator, 'jwt_verify_and_decode', return_value=make_lti13_resource_link_request
        ) as mock_verify_and_decode:
            _ = await authenticator.authenticate(request_handler, None)
            assert mock_verify_and_decode.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_validate_launch_request(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Does the authenticator invoke the LTI13Validator validate_launch_request method?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(
            LTI13LaunchValidator, 'validate_launch_request', return_value=True
        ) as mock_verify_authentication_request:
            _ = await authenticator.authenticate(request_handler, None)
            assert mock_verify_authentication_request.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti_utils_normalize_string(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Does the authenticator invoke the LTIUtils normalize_string method?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            with patch.object(LTIUtils, 'normalize_string', return_value=True) as mock_normalize_string:
                _ = await authenticator.authenticate(request_handler, None)
                assert mock_normalize_string.called


@pytest.mark.asyncio
async def test_authenticator_returns_course_id_in_auth_state_with_valid_resource_link_request(
    auth_state_dict, make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we get a valid course_id when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['course_id'] == 'intro101'


@pytest.mark.asyncio
async def test_authenticator_returns_auth_state_name_from_lti13_email_claim(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we get a valid username when only including an email to the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    lti13_json = make_lti13_resource_link_request
    lti13_json['name'] = ''
    lti13_json['given_name'] = ''
    lti13_json['family_name'] = ''
    lti13_json['email'] = 'usertest@example.com'
    with patch.object(RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(lti13_json)):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['name'] == 'usertest'


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_with_name(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we get a valid username when only including the name in the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['name'] = 'Foo'
    make_lti13_resource_link_request['given_name'] = ''
    make_lti13_resource_link_request['family_name'] = ''
    make_lti13_resource_link_request['email'] = ''
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['name'] == 'foo'


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_with_given_name(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we get a valid username when only including the given name in the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['name'] = ''
    make_lti13_resource_link_request['given_name'] = 'Foo Bar'
    make_lti13_resource_link_request['family_name'] = ''
    make_lti13_resource_link_request['email'] = ''
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['name'] == 'foobar'


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_family_name(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we get a valid username when only including the family name in the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['name'] = ''
    make_lti13_resource_link_request['given_name'] = ''
    make_lti13_resource_link_request['family_name'] = 'Family name'
    make_lti13_resource_link_request['email'] = ''
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)

            assert result['name'] == 'familyname'


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_person_sourcedid(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we get a valid username when only including lis person sourcedid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['name'] = ''
    make_lti13_resource_link_request['given_name'] = ''
    make_lti13_resource_link_request['family_name'] = ''
    make_lti13_resource_link_request['email'] = ''
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/lis']['person_sourcedid'] = 'abc123'

    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)

            assert result['name'] == 'abc123'


@pytest.mark.asyncio
async def test_authenticator_returns_workspace_type_in_auth_state(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we get a valid lms_user_id in the auth_state when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)

            assert result['auth_state'].get('workspace_type') == 'notebook'


@pytest.mark.asyncio
async def test_authenticator_returns_learner_role_in_auth_state(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the learner role in the auth_state when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request[
        'https://purl.imsglobal.org/spec/lti/claim/roles'
    ] = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner'

    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == 'Learner'


@pytest.mark.asyncio
async def test_authenticator_returns_instructor_role_in_auth_state_with_instructor_role(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the instructor role in the auth_state when receiving a valid resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/roles'] = [
        'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor'
    ]
    id_token = build_lti13_jwt_id_token(make_lti13_resource_link_request)

    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == 'Instructor'


@pytest.mark.asyncio
async def test_authenticator_returns_student_role_in_auth_state_with_learner_role(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the student role in the auth_state when receiving a valid resource link request with the Learner role?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    # set our role to test
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/roles'] = [
        'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner'
    ]
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == 'Learner'


@pytest.mark.asyncio
async def test_authenticator_returns_student_role_in_auth_state_with_student_role(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the student role in the auth_state when receiving a valid resource link request with the Student role?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    # set our role to test
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/roles'] = [
        'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student'
    ]

    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == 'Learner'


@pytest.mark.asyncio
async def test_authenticator_returns_learner_role_in_auth_state_with_empty_roles(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the learner role in the auth_state when receiving resource link request
    with empty roles?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/roles'] = []
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['user_role'] == 'Learner'


@pytest.mark.asyncio
async def test_authenticator_returns_default_workspace_type_with_unrecognized_workspace_type_in_custom_claim(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the default notebook image when the workspace type is unrecognized?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    # set our workspace_type custom field with a fake value
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/custom']['workspace_type'] = 'fake'
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == 'notebook'


@pytest.mark.asyncio
async def test_authenticator_returns_default_workspace_type_with_missing_workspace_type_in_custom_claim(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the default notebook image when the workspace type is missing?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    # remove the custom claim
    del make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/custom']['workspace_type']
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == 'notebook'


@pytest.mark.asyncio
async def test_authenticator_returns_notebook_as_workspace_type_in_auth_state_if_the_custom_claim_contains_this_value(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the workspace image to the notebook image when setting the workspace type to notebook?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/custom']['workspace_type'] = 'notebook'
    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == 'notebook'


@pytest.mark.asyncio
async def test_authenticator_returns_rstudio_workspace_image_with_rstudio_workspace_type_in_auth_state(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the workspace image to the rstudio image when setting the workspace type to rstudio?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/custom']['workspace_type'] = 'rstudio'

    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == 'rstudio'


@pytest.mark.asyncio
async def test_authenticator_returns_theia_workspace_image_with_theia_workspace_type_in_auth_state(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the workspace image to the theia image when setting the workspace type to tbeia?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/custom']['workspace_type'] = 'theia'

    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == 'theia'


@pytest.mark.asyncio
async def test_authenticator_returns_vscode_workspace_image_with_vscode_workspace_type_in_auth_state(
    make_lti13_resource_link_request, build_lti13_jwt_id_token, make_mock_request_handler
):
    """
    Do we set the workspace image to the vscode image when setting the workspace type to vscode?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(RequestHandler, authenticator=authenticator)
    make_lti13_resource_link_request['https://purl.imsglobal.org/spec/lti/claim/custom']['workspace_type'] = 'vscode'

    with patch.object(
        RequestHandler, 'get_argument', return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request)
    ):
        with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
            result = await authenticator.authenticate(request_handler, None)
            assert result['auth_state']['workspace_type'] == 'vscode'
