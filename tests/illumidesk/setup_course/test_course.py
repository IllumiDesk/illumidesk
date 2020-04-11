import os, sys
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch
from unittest.mock import Mock, MagicMock
from docker.errors import NotFound
from illumidesk.setup_course.course import Course


@pytest.fixture(scope="function")
def setup_environ(monkeypatch, tmp_path):
    monkeypatch.setenv('NFS_ROOT', str(tmp_path))
    monkeypatch.setenv('NB_UID', '10001')
    monkeypatch.setenv('NB_GID', '100')

@pytest.fixture(scope="function")
def docker_containers():
    docker_client = Mock(spec='docker.DockerClient')

    def _container_not_exists(name):
        raise NotFound(f'container: {name} not exists')

    docker_client.containers = MagicMock()
    docker_client.containers.get.side_effect = lambda name: _container_not_exists(name)


def test_initializer_requires_arguments():
    with pytest.raises(TypeError):
        Course()

def test_initializer_set_course_id(setup_environ):    
    course = Course(org='org1', course_id='example', domain='example.com')
    assert course.course_id is not None
    assert course.course_id == 'example'

def test_initializer_set_org(setup_environ):    
    course = Course(org='org1', course_id='example', domain='example.com')
    assert course.org is not None
    assert course.org == 'org1'

def test_initializer_set_domain(setup_environ):    
    course = Course(org='org1', course_id='example', domain='example.com')
    assert course.domain is not None
    assert course.domain == 'example.com'

def test_grader_name_is_correct(setup_environ):    
    course = Course(org='org1', course_id='example', domain='example.com')
    assert course.grader_name is not None
    assert course.grader_name == f'grader-{course.course_id}'

def test_grader_root_path_is_valid(setup_environ):    
    course = Course(org='org1', course_id='example', domain='example.com')
    assert course.grader_root is not None
    assert course.grader_root == Path(
            os.environ.get('NFS_ROOT'),
            course.org,
            'home',
            course.grader_name,
        )

def test_course_path_is_a_grader_root_subfolder(setup_environ):
    course = Course(org='org1', course_id='example', domain='example.com')
    assert course.course_root is not None
    assert course.course_root == Path(course.grader_root, course.course_id)

def test_new_course_has_a_token(setup_environ):
    course = Course(org='org1', course_id='example', domain='example.com')
    assert course.token is not None

def test_a_course_contains_service_config_well_formed(setup_environ):
    course = Course(org='org1', course_id='example', domain='example.com')
    service_config = course.get_service_config()
    assert type(service_config) == dict
    assert 'name' in service_config
    assert 'url' in service_config
    assert 'admin' in service_config
    assert 'api_token' in service_config

def test_a_course_contains_service_config_with_correct_values(setup_environ):
    course = Course(org='org1', course_id='example', domain='example.com')
    service_config = course.get_service_config()    
    assert service_config['name'] == course.course_id
    assert service_config['url'] == f'http://{course.grader_name}:8888'
    assert service_config['admin'] == True
    assert service_config['api_token'] == course.token

@patch('docker.DockerClient.containers')
def test_should_setup_method_returns_true_if_container_does_not_exist(mock_docker, setup_environ):
    course = Course(org='org1', course_id='example', domain='example.com')
    def _container_not_exists(name):
        raise NotFound(f'container: {name} not exists')
    mock_docker.get.side_effect = lambda name: _container_not_exists(name)
    assert course.should_setup() == True

def test_course_exchange_root_directory_is_created(setup_environ, docker_containers):
    course = Course(org='org1', course_id='example', domain='example.com')
    with patch('shutil.chown', autospec=True):
        course.create_directories()
        assert course.exchange_root.exists()

def test_course_root_directory_is_created(setup_environ, docker_containers):
    course = Course(org='org1', course_id='example', domain='example.com')
    with patch('shutil.chown', autospec=True):
        course.create_directories()
        assert course.course_root.exists()

def test_course_jupyter_config_path_is_created(setup_environ, docker_containers):
    course = Course(org='org1', course_id='example', domain='example.com')
    with patch('shutil.chown', autospec=True):
        course.create_directories()
        assert course.jupyter_config_path.exists()

def test_course_nbgrader_config_path_is_created(setup_environ, docker_containers):
    course = Course(org='org1', course_id='example', domain='example.com')
    with patch('shutil.chown', autospec=True):
        course.create_directories()
        assert course.nbgrader_config_path.exists()
