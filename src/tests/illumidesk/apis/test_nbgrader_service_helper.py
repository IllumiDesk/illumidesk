import os
from pathlib import Path
import shutil
import pytest

from unittest.mock import patch

from illumidesk.apis.nbgrader_service import NbGraderServiceHelper
from illumidesk.apis.nbgrader_service import nbgrader_format_db_url


class TestNbGraderServiceBaseHelper:
    def setup_method(self, method):
        """
        Setup method to initialize objects/properties used for the tests
        """
        self.course_id = 'PS- ONE'
        self.sut = NbGraderServiceHelper(self.course_id)

    def test_course_id_required_otherwise_raises_an_error(self):
        """
        Does the initializer accept empty or none value for course_id?
        """
        with pytest.raises(ValueError):
            NbGraderServiceHelper('')

    def test_course_id_is_normalized_in_the_constructor(self):
        """
        Does the course-id value is normalized?
        """
        assert self.sut.course_id == 'ps-one'

    @patch('shutil.chown')
    @patch('os.makedirs')
    @patch('illumidesk.apis.nbgrader_service.Gradebook')
    def test_create_assignment_in_nbgrader_uses_the_assignment_name_normalized(
        self, mock_gradebook, mock_makedirs, mock_chown
    ):
        """
        Does the assignment is created with normalized value?
        """
        self.sut.create_assignment_in_nbgrader('LAB 1')
        assert mock_gradebook.return_value.__enter__.return_value.update_or_create_assignment.called
        assert mock_gradebook.return_value.__enter__.return_value.update_or_create_assignment.call_args[0][0] == 'lab1'

    @patch('os.makedirs')
    @patch('pathlib.Path.mkdir')
    @patch('illumidesk.apis.nbgrader_service.Gradebook')
    def test_create_assignment_in_nbgrader_method_fixes_source_directory_permissions(
        self, mock_gradebook, mock_path_mkdir, mock_makedirs
    ):
        """
        Does the assignment source directory is created and it is fixed with the correct file permissions?
        """
        with patch.object(shutil, 'chown') as mock_chown:
            self.sut.create_assignment_in_nbgrader('lab-abc')
            source_dir = os.path.abspath(Path(self.sut.course_dir, 'source'))
            mock_chown.assert_any_call(source_dir, user=10001, group=100)

    @patch('os.makedirs')
    @patch('pathlib.Path.mkdir')
    @patch('illumidesk.apis.nbgrader_service.Gradebook')
    def test_create_assignment_in_nbgrader_method_fixes_assignment_directory_permissions(
        self, mock_gradebook, mock_path_mkdir, mock_makedirs
    ):
        """
        Does the assignment directory is fixed with the correct file permissions?
        """
        with patch.object(shutil, 'chown') as mock_chown:
            self.sut.create_assignment_in_nbgrader('lab-abc')
            assignment_dir = os.path.abspath(Path(self.sut.course_dir, 'source', 'lab-abc'))
            mock_chown.assert_any_call(assignment_dir, user=10001, group=100)

    @patch('shutil.chown')
    @patch('pathlib.Path.mkdir')
    @patch('illumidesk.apis.nbgrader_service.Gradebook')
    def test_add_user_to_nbgrader_gradebook_raises_error_when_empty(self, mock_gradebook, mock_path_mkdir, mock_chown):
        """
        Does add_user_to_nbgrader_gradebook method accept an empty username, or lms user id?
        """
        with pytest.raises(ValueError):
            self.sut.add_user_to_nbgrader_gradebook(username='', lms_user_id='abc123')

        with pytest.raises(ValueError):
            self.sut.add_user_to_nbgrader_gradebook(username='user1', lms_user_id='')


class TestNbGraderServiceHelper:
    def test_nbgrader_format_db_url_method_uses_env_vars_to_get_db_url(self, monkeypatch):
        monkeypatch.setattr('illumidesk.apis.nbgrader_service.nbgrader_db_host', 'test_host')
        monkeypatch.setattr('illumidesk.apis.nbgrader_service.nbgrader_db_password', 'test_pwd')
        monkeypatch.setattr('illumidesk.apis.nbgrader_service.nbgrader_db_user', 'test_user')
        monkeypatch.setattr('illumidesk.apis.nbgrader_service.org_name', 'org-dummy')

        assert nbgrader_format_db_url('Course 1') == 'postgresql://test_user:test_pwd@test_host:5432/org-dummy_course1'
