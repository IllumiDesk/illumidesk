# -*- coding: utf-8 -*-

import base64
import io
import os
import sys
import json
import pytest

from os.path import join
from textwrap import dedent
from nbformat import current_nbformat

from nbgrader.api import Gradebook, MissingEntry
from nbgrader.utils import remove
from nbgrader.nbgraderformat import reads
from nbgrader.tests import run_nbgrader
from nbgrader.tests.apps.conftest import course_dir, db, exchange, temp_cwd
from ...tests import run_async_nbgrader
from nbgrader.tests.apps.base import BaseTestApp


class TestNbGraderAutograde(BaseTestApp):
    def test_grade(self, cache, course_dir, db, exchange):
        """Can files be graded?"""

        assignment_id = "ps1"
        student_id = "foo-student"
        notebook_dir, course_id = course_dir.rsplit("/", 1)

        with open(join(notebook_dir, "nbgrader_config.py"), "a") as fh:
            fh.write(f"""\nc.CourseDirectory.course_id = "{course_id}"\n""")
            fh.write(f"""c.CourseDirectory.db_url = "{db}"\n""")
            fh.write(
                f"""c.CourseDirectory.db_assignments = [dict(name='{assignment_id}', duedate='2015-02-02 14:58:23.948203 America/Los_Angeles')]\n"""
            )
            fh.write(f"""c.CourseDirectory.db_students = [dict(id="{student_id}")]\n""")
            fh.write(f"""c.Exchange.root = "{exchange}"\n""")
            fh.write(f"""c.Exchange.cache = "{cache}"\n""")

        self._copy_file(
            join(notebook_dir, "nbgrader_config.py"),
            join(notebook_dir, ".jupyter", "nbgrader_config.py"),
        )
        self._copy_file(
            join("files", "submitted-unchanged.ipynb"),
            join(notebook_dir, course_id, "source", assignment_id, "p1.ipynb"),
        )
        run_nbgrader(["generate_assignment", assignment_id, "--db", db])

        self._copy_file(
            join("files", "submitted-changed.ipynb"),
            join(
                notebook_dir,
                course_id,
                "submitted",
                student_id,
                assignment_id,
                "p1.ipynb",
            ),
        )
        message = json.dumps(
            {
                "data": base64.b64encode(
                    json.dumps(
                        {
                            "body": {
                                "action": "autograde",
                                "notebook_dir": notebook_dir,
                                "course_id": course_id,
                                "assignment_id": assignment_id,
                                "student_id": student_id,
                            }
                        }
                    ).encode("utf-8")
                ).decode("ascii")
            }
        )
        run_async_nbgrader(["process_message", message, "--db", db], 0, None, True)
