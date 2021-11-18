# coding: utf-8

import base64
import json
import os
import traceback

from traitlets import default
from nbgrader.apps.baseapp import NbGrader
from nbgrader.coursedir import CourseDirectory
from ..helpers import chdir
from ..helpers import get_nbgrader_api


aliases = {
    "log-level": "Application.log_level",
    "db": "CourseDirectory.db_url",
}
flags = {}


# JupyterHub settings
JUPYTERHUB_API_URL = os.environ.get("JUPYTERHUB_API_URL") or "http://hub:8081/hub/api"
JUPYTERHUB_BASE_URL = os.environ.get("JUPYTERHUB_BASE_URL") or "/"


class ProcessMessageApp(NbGrader):
    """App to handle amqp messages from Argo"""

    name = "async_nbgrader-process-message"

    aliases = aliases

    @default("classes")
    def _classes_default(self):
        classes = super(ProcessMessageApp, self)._classes_default()
        classes.append(ProcessMessageApp)
        return classes

    def start(self):
        """Handler for processing mesage, message is passed as first argument, it is received in self.extra_args[0]"""
        super(ProcessMessageApp, self).start()
        if len(self.extra_args) == 0 or self.extra_args[0] == "":
            self.fail("message is missing")
        message = json.loads(self.extra_args[0])
        encoded_message = message["data"]
        self.log.info("message " + encoded_message)
        missing_padding = len(encoded_message) % 4
        if missing_padding > 0:
            encoded_message += b"=" * (4 - missing_padding)
        body = json.loads(base64.b64decode(encoded_message).decode("utf-8")).get("body")
        if body == None:
            self.fail("body is missing")
        action = body.get("action")
        notebook_dir = body.get("notebook_dir")
        course_id = body.get("course_id")
        grader_name = f"grader-{course_id}"
        os.environ["NB_USER"] = grader_name
        os.environ["JUPYTERHUB_USER"] = grader_name
        os.environ["JUPYTERHUB_SERVICE_NAME"] = course_id
        os.environ["JUPYTERHUB_CLIENT_ID"] = f"service-{course_id}"
        os.environ["JUPYTERHUB_SERVICE_PREFIX"] = f"/services/{course_id}/"
        os.environ["JUPYTERHUB_API_URL"] = JUPYTERHUB_API_URL
        os.environ["JUPYTERHUB_BASE_URL"] = JUPYTERHUB_BASE_URL
        os.environ["JUPYTERHUB_API_TOKEN"] = body.get("JUPYTERHUB_API_TOKEN")
        os.environ["NB_GID"] = str(body.get("NB_GID"))
        os.environ["NB_UID"] = str(body.get("NB_UID"))
        os.environ["JUPYTER_CONFIG_DIR"] = notebook_dir + "/.jupyter"
        try:
            with chdir(notebook_dir + "/" + course_id):
                api = get_nbgrader_api(notebook_dir, course_id)
                api.log = self.log
                api.log_level = 0
                if action == "autograde":
                    assignment_id = body.get("assignment_id")
                    student_id = body.get("student_id")
                    self.log.info("Running Autograde")
                    self.log.info("DB url = " + api.coursedir.db_url)
                    api.autograde(assignment_id, student_id)
                    self.log.info("Autograde Finished")
                else:
                    self.fail("message is missing")
        except Exception as e:
            self.log.info("Error caught")
            self.log.error(traceback.format_exc())
            self.fail("failure in processing")
