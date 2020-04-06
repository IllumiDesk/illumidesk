from jupyterhub.tests.mocking import MockSpawner


_group_name_counter = 0


def new_group_name(prefix='testgroup'):
    """
    Return a new unique group name
    """
    global _group_name_counter
    _group_name_counter += 1
    return '{}-{}'.format(prefix, _group_name_counter)


@fixture
def group_name():
    """
    Allocate a temporary group name
    unique each time the fixture is used
    """
    yield new_group_name()


@mark.group
def _requests(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://someurl.com/test.json':
        return MockResponse({'key1': 'value1'}, 200)
    elif args[0] == 'http://someotherurl.com/anothertest.json':
        return MockResponse({'key2': 'value2'}, 200)

    return MockResponse(None, 404)
