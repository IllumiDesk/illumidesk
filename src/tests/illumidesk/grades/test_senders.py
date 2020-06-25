import json
from pathlib import Path

import pytest

from unittest.mock import patch

from illumidesk.grades.sender_controlfile import LTIGradesSenderControlFile
from illumidesk.grades.senders import LTIGradeSender
from illumidesk.grades.exceptions import GradesSenderCriticalError
from illumidesk.grades.exceptions import AssignmentWithoutGradesError
from illumidesk.grades.exceptions import GradesSenderMissingInfoError


@pytest.mark.asyncio
async def test_grades_sender_raises_a_critical_error_when_gradebook_does_not_exist(tmp_path):
    """
    Does the sender raises an error when the gradebook db is not found?
    """
    sender_controlfile = LTIGradeSender('course1', 'problem1')
    with pytest.raises(GradesSenderCriticalError):
        await sender_controlfile.send_grades()

@pytest.mark.asyncio
async def test_grades_sender_raises_an_error_if_there_are_no_grades(tmp_path):
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
