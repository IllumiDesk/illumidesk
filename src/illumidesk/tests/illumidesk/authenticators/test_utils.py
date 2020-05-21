import re

from tornado.web import RequestHandler

from unittest.mock import Mock

from illumidesk.authenticators.utils import LTIUtils


def test_normalize_name_for_containers_with_long_name():
    """
    Does a container name with more than 20 characters get normalized?
    """
    container_name = 'this_is_a_really_long_container_name'
    utils = LTIUtils()
    normalized_container_name = utils.normalize_name_for_containers(container_name)

    assert len(normalized_container_name) <= 20


def test_normalize_name_for_containers_with_special_characters():
    """
    Does a container name with with special characters get normalized?
    """
    container_name = '#$%_this_is_a_container_name'
    utils = LTIUtils()
    normalized_container_name = utils.normalize_name_for_containers(container_name)
    regex = re.compile('[@!#$%^&*()<>?/\\|}{~:]')

    assert regex.search(normalized_container_name) is None


def test_normalize_name_for_containers_with_first_letter_as_alphanumeric():
    """
    Does a container name with start with an alphanumeric character?
    """
    container_name = '___this_is_a_container_name'
    utils = LTIUtils()
    normalized_container_name = utils.normalize_name_for_containers(container_name)
    regex = re.compile('_.-')
    first_character = normalized_container_name[0]
    assert first_character != regex.search(normalized_container_name)


def test_get_protocol_with_more_than_one_value():
    """
    Are we able to determine the original protocol from the client's launch request?
    """
    utils = LTIUtils()
    handler = Mock(
        spec=RequestHandler, request=Mock(headers={'x-forwarded-proto': 'https,http,http'}, protocol='https',),
    )
    expected = 'https'
    protocol = utils.get_client_protocol(handler)

    assert expected == protocol


def test_convert_request_arguments_to_dict():
    """
    Do the items from a request object convert to a dict with decoded values?
    """
    utils = LTIUtils()
    arguments = {
        'key1': [b'value1'],
        'key2': [b'value2'],
        'key3': [b'value3'],
    }
    expected = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
    }
    result = utils.convert_request_to_dict(arguments)

    assert expected == result


def test_get_lms_access_token():
    """
    Are we able to get a valid access token from an LTI 1.3 compatible platform?
    """
    utils = LTIUtils()
    iss = 'https://canvas.instructure.com'
    token_url = 'https://canvas.instructure.com/login/oauth2/token'
    private_key = '/my/private/key.pem'
    client_id = '125900000000000071'

    expected = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
    }
    arguments = ({'foo': 'bar'}).encode()
    result = utils.convert_request_to_dict(arguments)

    assert expected == result


# valid token params
# is jwt.encode called
# are the params used to build the body payload correct
# does the method return a properly formatted json
