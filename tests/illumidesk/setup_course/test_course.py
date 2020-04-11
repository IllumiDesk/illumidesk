import os
import pytest
from pathlib import Path
from illumidesk.setup_course.course import Course


@pytest.fixture(scope="function")
def setup_environ(monkeypatch):
    monkeypatch.setenv('NFS_ROOT', '/home')
    monkeypatch.setenv('NB_UID', '10001')
    monkeypatch.setenv('NB_GID', '100')

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