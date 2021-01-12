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
