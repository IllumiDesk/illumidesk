import pytest
from illumideskdummyauthenticator.validators import IllumiDeskDummyValidator
from tornado.web import HTTPError


def test_basic_login_request(make_dummy_authentication_request_args):
    """
    Does a standard login request work?
    """
    args = make_dummy_authentication_request_args()

    validator = IllumiDeskDummyValidator()

    assert validator.validate_login_request(args)


@pytest.mark.parametrize(
    "invalid,dummy_arg",
    [
        ("", "assignment_name"),
        ("", "course_id"),
        ("", "lms_user_id"),
        ("", "username"),
        ("", "password"),
    ],
)
def test_login_with_none_or_empty_required_args(
    invalid,
    dummy_arg,
    make_dummy_authentication_request_args,
):
    """
    Does the launch request work with an empty or None oauth_signature_method value?
    """
    args = make_dummy_authentication_request_args()

    validator = IllumiDeskDummyValidator()

    with pytest.raises(HTTPError):
        args[dummy_arg] = invalid
        validator.validate_login_request(args)
