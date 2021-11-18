import json
import os
import pika

from nbgrader.server_extensions.formgrader.apihandlers import AutogradeHandler
from nbgrader.server_extensions.formgrader.base import check_notebook_dir
from nbgrader.server_extensions.formgrader.base import check_xsrf
from notebook.notebookapp import NotebookApp
from notebook.utils import url_path_join as ujoin
from tornado import web


class AsyncAutogradeHandler(AutogradeHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def post(self, assignment_id: str, student_id: str) -> None:
        """Handler for processing autograding request, queues autograding task in amqp"""
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(os.environ.get("RABBITMQ_HOST", "argo-rabbitmq-service")),
        )
        channel = connection.channel()
        namespace = os.environ.get("NAMESPACE")
        channel.exchange_declare(
            exchange=namespace,
            exchange_type="topic",
            passive=False,
            durable=True,
        )
        body = json.dumps(
            {
                "action": "autograde",
                "notebook_dir": self.settings["notebook_dir"],
                "course_id": self.api.course_id,
                "assignment_id": assignment_id,
                "student_id": student_id,
                "NB_UID": os.environ.get("NB_UID"),
                "NB_GID": os.environ.get("NB_GID"),
                "JUPYTERHUB_API_TOKEN": os.environ.get("JUPYTERHUB_API_TOKEN"),
            }
        )
        channel.basic_publish(
            exchange=namespace,
            routing_key="autograde_events",
            body=body,
        )
        self.write(
            json.dumps(
                {
                    "success": True,
                    "queued": True,
                    "message": "Submission Autograding queued",
                }
            )
        )


handlers = [
    (r"/formgrader/api/submission/([^/]+)/([^/]+)/autograde", AsyncAutogradeHandler),
]


def rewrite(nbapp: NotebookApp, x: str) -> str:
    """Rewrites a path to remove the trailing forward slash (/).

    Args:
        nbapp (NotebookApp): The Jupyter Notebook application instance.
        x (str): The path to rewrite.

    Returns:
        str: the re written path.
    """
    web_app = nbapp.web_app
    pat = ujoin(web_app.settings["base_url"], x[0].lstrip("/"))
    return (pat,) + x[1:]


def load_jupyter_server_extension(nbapp: NotebookApp) -> None:
    """Start background processor

    Args:
      nbapp (NotebookApp): The Jupyter Notebook application instance.
    """
    if os.environ.get("NBGRADER_ASYNC_MODE", "true") == "true":
        nbapp.log.info("Starting background processor for nbgrader serverextension")
        nbapp.web_app.add_handlers(".*$", [rewrite(nbapp, x) for x in handlers])
    else:
        nbapp.log.info("Skipping background processor for nbgrader serverextension")
