import re

import pytest

from tornado.web import RequestHandler

from unittest.mock import Mock

from illumidesk.authenticators.utils import LTIUtils


def test_normalize_string_return_false_with_missing_name():
    """
    Does a missing container name raise a value error?
    """
    container_name = ''
    utils = LTIUtils()
    with pytest.raises(ValueError):
        utils.normalize_string(container_name)


def test_normalize_string_with_long_name():
    """
    Does a container name with more than 20 characters get normalized?
    """
    container_name = 'this_is_a_really_long_container_name'
    utils = LTIUtils()
    normalized_container_name = utils.normalize_string(container_name)

    assert len(normalized_container_name) <= 20


def test_normalize_string_with_special_characters():
    """
    Does a container name with with special characters get normalized?
    """
    container_name = '#$%_this_is_a_container_name'
    utils = LTIUtils()
    normalized_container_name = utils.normalize_string(container_name)
    regex = re.compile('[@!#$%^&*()<>?/\\|}{~:]')

    assert regex.search(normalized_container_name) is None


def test_normalize_string_with_first_letter_as_alphanumeric():
    """
    Does a container name with start with an alphanumeric character?
    """
    container_name = '___this_is_a_container_name'
    utils = LTIUtils()
    normalized_container_name = utils.normalize_string(container_name)
    regex = re.compile('_.-')
    first_character = normalized_container_name[0]
    assert first_character != regex.search(normalized_container_name)


def test_normalize_string_raises_value_error_with_missing_name():
    """
    Does a missing container name raise a value error?
    """
    container_name = ''
    utils = LTIUtils()

    with pytest.raises(ValueError):
        utils.normalize_string(container_name)


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


def test_convert_request_arguments_with_one_encoded_item_to_dict():
    """
    Do the items from a request object with one item per encoded value convert to a dict with decoded values?
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


def test_convert_request_arguments_with_more_than_one_encoded_item_to_dict():
    """
    Do the items from a request object with more than one item per encoded value convert to a dict with decoded values
    where the dict has one value per item?
    """
    utils = LTIUtils()
    arguments = {
        'key1': [b'value1', b'valueA'],
        'key2': [b'value2', b'valueB'],
        'key3': [b'value3', b'valueC'],
    }
    expected = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
    }
    result = utils.convert_request_to_dict(arguments)

    assert expected == result


def test_email_to_username_retrieves_only_username_part_before_at_symbol():
    """
    Does the email_to_username method remove all after @?
    """
    email = 'user1@example.com'

    utils = LTIUtils()
    # act
    result = utils.email_to_username(email)
    assert result == 'user1'


def test_email_to_username_converts_username_in_lowecase():
    """
    Does the email_to_username method convert to lowecase the username part?
    """
    email = 'USER_name1@example.com'

    utils = LTIUtils()
    # act
    result = utils.email_to_username(email)
    assert result == 'user_name1'


def test_email_to_username_retrieves_only_first_part_before_plus_symbol():
    """
    Does the email_to_username method remove '+' symbol?
    """
    email = 'user+name@example.com'

    utils = LTIUtils()
    # act
    result = utils.email_to_username(email)
    assert result == 'user'
