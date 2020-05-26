import pytest

from illumidesk.setup_course.utils import SetupUtils


def test_setup_utils_properties_after_initialization(setup_utils_environ):
    """
    Does the initializer properly set the illumidesk directory property?
    """
    setup_utils = SetupUtils()

    assert setup_utils.docker_client is not None
    assert setup_utils.jupyterhub_container_name == 'jupyterhub'
    assert setup_utils.illumidesk_dir == '/home/foo/illumidesk_deployment'


@pytest.mark.asyncio
async def test_create_setup_utils_without_init_env_vars():
    """
    Do we get a type error when attempting to create a SetupUtils instance without the correct
    initialization variables?
    """
    with pytest.raises(TypeError):
        SetupUtils()


def test_initializer_setup_utils(setup_utils_environ):
    """
    Does the initializer properly set the illumidesk directory property?
    """
    setup_utils = SetupUtils()
    assert setup_utils.illumidesk_dir is not None
    assert setup_utils.illumidesk_dir != ''
    assert setup_utils.illumidesk_dir == '/home/foo/illumidesk_deployment'
