import os
from pathlib import Path
import shutil
import pytest

from unittest.mock import patch

from illumidesk.apis.nbgrader_service import NbGraderServiceHelper


def test_course_id_required_otherwise_raises_an_error():
    with pytest.raises(ValueError):
        NbGraderServiceHelper('')


@patch('shutil.chown')
@patch('pathlib.Path.mkdir')
@patch('illumidesk.apis.nbgrader_service.Gradebook')
def test_course_id_is_normalized_in_the_constructor(mock_gradebook, mock_path_mkdir, mock_chown):
    sut = NbGraderServiceHelper('PS- ONE')
    assert sut.course_id == 'ps-one'


@patch('shutil.chown')
@patch('pathlib.Path.mkdir')
@patch('illumidesk.apis.nbgrader_service.Gradebook')
def test_graderbook_is_formed_correctly(mock_gradebook, mock_path_mkdir, mock_chown):
    course_id = 'PS- ONE 123'
    sut = NbGraderServiceHelper(course_id)
    assert str(sut.gradebook_path) == '/home/grader-ps-one123/ps-one123/gradebook.db'


@patch('shutil.chown')
@patch('pathlib.Path.mkdir')
@patch('illumidesk.apis.nbgrader_service.Gradebook')
def test_chown_is_called_to_fix_permissions(mock_gradebook, mock_path_mkdir, mock_chown):
    course_id = 'PS- ONE 123'
    NbGraderServiceHelper(course_id)
    assert mock_chown.called


@patch('shutil.chown')
@patch('pathlib.Path.mkdir')
@patch('illumidesk.apis.nbgrader_service.Gradebook')
def test_mkdir_is_called_with_grader_home_path(mock_gradebook, mock_path_mkdir, mock_chown):
    course_id = 'PS- ONE 123'
    NbGraderServiceHelper(course_id)
    assert mock_path_mkdir.called


@patch('os.makedirs')
@patch('shutil.chown')
@patch('pathlib.Path.mkdir')
@patch('illumidesk.apis.nbgrader_service.Gradebook')
def test_create_assignment_in_nbgrader_uses_the_assignment_name_normalized(
    mock_gradebook, mock_path_mkdir, mock_chown, mock_makedirs
):
    course_id = 'PS- ONE 123'
    sut = NbGraderServiceHelper(course_id)
    sut.create_assignment_in_nbgrader('LAB 1')
    assert mock_gradebook.return_value.__enter__.return_value.update_or_create_assignment.called
    assert mock_gradebook.return_value.__enter__.return_value.update_or_create_assignment.call_args[0][0] == 'lab1'


@patch('os.makedirs')
@patch('shutil.chown')
@patch('pathlib.Path.mkdir')
@patch('illumidesk.apis.nbgrader_service.Gradebook')
def test_new_instance_calls_chown_method_for_gradebook_path(
    mock_gradebook, mock_path_mkdir, mock_chown, mock_makedirs
):
    course_id = 'intro101'
    sut = NbGraderServiceHelper(course_id)
    assert mock_chown.called
    mock_chown.assert_called_once_with(str(sut.gradebook_path), user=10001, group=100)


@patch('os.makedirs')
@patch('pathlib.Path.mkdir')
@patch('illumidesk.apis.nbgrader_service.Gradebook')
def test_create_assignment_in_nbgrader_method_fixes_source_directory_permissions(
    mock_gradebook, mock_path_mkdir, mock_makedirs
):
    course_id = 'intro101'
    with patch.object(shutil, 'chown') as mock_chown:
        sut = NbGraderServiceHelper(course_id)
        sut.create_assignment_in_nbgrader('lab-abc')
        source_dir = os.path.abspath(Path(sut.course_dir, 'source'))
        mock_chown.assert_any_call(source_dir, user=10001, group=100)


@patch('os.makedirs')
@patch('pathlib.Path.mkdir')
@patch('illumidesk.apis.nbgrader_service.Gradebook')
def test_create_assignment_in_nbgrader_method_fixes_assignment_directory_permissions(
    mock_gradebook, mock_path_mkdir, mock_makedirs
):
    course_id = 'intro101'
    with patch.object(shutil, 'chown') as mock_chown:
        sut = NbGraderServiceHelper(course_id)
        sut.create_assignment_in_nbgrader('lab-abc')
        assignment_dir = os.path.abspath(Path(sut.course_dir, 'source', 'lab-abc'))
        mock_chown.assert_any_call(assignment_dir, user=10001, group=100)
