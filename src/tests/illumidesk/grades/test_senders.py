import json
from pathlib import Path

import pytest

from unittest.mock import patch

from illumidesk.grades.senders import LTIGradesSenderControlFile
from illumidesk.grades.senders import LTIGradeSender
from illumidesk.grades.exceptions import GradesSenderCriticalError
from illumidesk.grades.exceptions import AssignmentWithoutGradesError
from illumidesk.grades.exceptions import GradesSenderMissingInfoError


@pytest.fixture
def reset_file_loaded():
    LTIGradesSenderControlFile.FILE_LOADED = False


@pytest.mark.usefixtures('reset_file_loaded')
class TestLTIGradesSenderControlFile:
    def test_control_file_is_initialized_if_not_exists(self, tmp_path):
        """
        Does the LTIGradesSenderControlFile class initializes a file with an empty dict when it not exists?
        """
        sender_controlfile = LTIGradesSenderControlFile(tmp_path)
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


def test_grades_sender_raises_a_critical_error_when_gradebook_does_not_exist(tmp_path):
    """
    Does the sender raises an error when the gradebook db is not found?
    """
    sender_controlfile = LTIGradeSender('course1', 'problem1')
    with pytest.raises(GradesSenderCriticalError):
        await sender_controlfile.send_grades()


def test_grades_sender_raises_an_error_if_there_are_no_grades(tmp_path):
    """
    Does the sender raises an error when there are no grades?
    """
    sender_controlfile = LTIGradeSender('course1', 'problem1')
    # create a mock for our method that searches grades from gradebook.db
    with patch.object(LTIGradeSender, '_retrieve_grades_from_db', return_value=(lambda: 10, [])):
        with pytest.raises(AssignmentWithoutGradesError):
            await sender_controlfile.send_grades()


@pytest.mark.asyncio
async def test_grades_sender_raises_an_error_if_assignment_not_found_in_control_file(tmp_path):
    """
    Does the sender raise an error when there are grades but control file does not contain info related with
    the gradebook data?
    """
    sender_controlfile = LTIGradeSender('course1', 'problem1')
    _ = LTIGradesSenderControlFile(tmp_path)
    grades_nbgrader = [{'score': 10, 'lms_user_id': 'user1'}]
    # create a mock for our method that searches grades from gradebook.db
    with patch.object(LTIGradeSender, '_retrieve_grades_from_db', return_value=(lambda: 10, grades_nbgrader)):
        with pytest.raises(GradesSenderMissingInfoError):
            await sender_controlfile.send_grades()
