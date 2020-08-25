import os
import json
import pytest

from pathlib import Path

from unittest.mock import patch

from illumidesk.grades.sender_controlfile import LTIGradesSenderControlFile


@pytest.mark.usefixtures('grades_controlfile_reset_file_loaded')
class TestLTIGradesSenderControlFile:
    def test_control_file_is_initialized_if_not_exists(self, tmp_path):
        """
        Does the LTIGradesSenderControlFile class initializes a file with an empty dict when it does not exist?
        """
        sender_controlfile = LTIGradesSenderControlFile(tmp_path)
        assert Path(sender_controlfile.config_fullname).stat().st_size > 0
        with Path(sender_controlfile.config_fullname).open('r') as file:
            assert json.load(file) == {}

    def test_control_file_course_dir_is_created_if_not_exists(self, tmp_path):
        """
        Does the LTIGradesSenderControlFile class initializes a file with an empty dict when it does not exist?
        """
        course_dir = os.path.join(tmp_path, 'my-course')
        sender_controlfile = LTIGradesSenderControlFile(course_dir)
        assert Path(course_dir).exists()
        assert Path(sender_controlfile.config_fullname).stat().st_size > 0
        with Path(sender_controlfile.config_fullname).open('r') as file:
            assert json.load(file) == {}

    def test_sender_control_file_indicates_when_file_was_loaded(self, tmp_path):
        """
        Does the LTIGradesSenderControlFile class indicates when the file was loaded?
        """
        assert LTIGradesSenderControlFile.FILE_LOADED is False
        sender_controlfile = LTIGradesSenderControlFile(tmp_path)
        assert LTIGradesSenderControlFile.FILE_LOADED is True

    def test_sender_control_file_initializes_its_content_at_fist_time(self, tmp_path):
        """
        Does the LTIGradesSenderControlFile class indicates when the file was loaded?
        """

        def _change_flag():
            LTIGradesSenderControlFile.FILE_LOADED = True

        with patch.object(LTIGradesSenderControlFile, '_loadFromFile', return_value=None) as mock_loadFromFileMethod:
            mock_loadFromFileMethod.side_effect = _change_flag
            sender_controlfile = LTIGradesSenderControlFile(tmp_path)
            assert LTIGradesSenderControlFile.FILE_LOADED is True
            # second time invocation
            _ = LTIGradesSenderControlFile(tmp_path)
            assert mock_loadFromFileMethod.call_count == 1

    def test_sender_control_file_registers_new_assignment(self, tmp_path):
        """
        Does the LTIGradesSenderControlFile class registers new assignment data correctly?
        """
        # arrange
        sender_controlfile = LTIGradesSenderControlFile(tmp_path)
        assignment_name = 'Assignment1'
        lis_outcome_service_url = 'https://example.instructure.com/api/lti/v1/tools/111/grade_passback'
        lms_user_id = 'user1'
        lis_result_sourcedid = 'uniqueIDToIdentifyUserWithinAssignment'
        # act
        sender_controlfile.register_data(assignment_name, lis_outcome_service_url, lms_user_id, lis_result_sourcedid)
        # assert
        saved = sender_controlfile.get_assignment_by_name(assignment_name)
        # item was saved
        assert saved is not None
        # url is the same that passed value
        assert saved['lis_outcome_service_url'] == lis_outcome_service_url
        # students property is a list
        assert type(saved['students']) == list
        # student was saved
        assert [s for s in saved['students'] if s['lms_user_id'] == lms_user_id]

    def test_sender_control_file_registers_multiple_students_in_same_assignment(self, tmp_path):
        """
        Does the LTIGradesSenderControlFile class registers students at same assignment level?
        """
        # arrange
        sender_controlfile = LTIGradesSenderControlFile(tmp_path)
        assignment_name = 'Assignment1'
        lis_outcome_service_url = 'https://example.instructure.com/api/lti/v1/tools/111/grade_passback'
        lms_user_id = 'user1'
        lis_result_sourcedid = 'uniqueIDToIdentifyUserWithinAssignment'
        # act
        sender_controlfile.register_data(assignment_name, lis_outcome_service_url, lms_user_id, lis_result_sourcedid)
        # add SECOND student
        sender_controlfile.register_data(assignment_name, lis_outcome_service_url, 'user2', lis_result_sourcedid)
        # assert
        saved = sender_controlfile.get_assignment_by_name(assignment_name)
        assert len(saved['students']) == 2
        # both students in test was saved with same lis_result_sourcedid value
        assert set([s['lms_user_id'] for s in saved['students']]) == {'user1', 'user2'}
