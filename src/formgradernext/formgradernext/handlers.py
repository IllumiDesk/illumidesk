import os
import sys

import requests
from jinja2 import BaseLoader
from jinja2 import Environment
from nbgrader.server_extensions.formgrader.base import BaseHandler
from nbgrader.server_extensions.formgrader.base import check_notebook_dir
from nbgrader.server_extensions.formgrader.base import check_xsrf
from notebook.notebookapp import NotebookApp
from notebook.utils import url_path_join as ujoin
from tornado import web

from .middleware import coop_coep_headers

DEFAULT_LMS_VERSION = os.environ.get("DEFAULT_LMS_VERSION") or "0.3.0"


def get_template(version: str) -> str:
    """Gets the template based on the version of the LMS package."""
    template_response = requests.get(
        f"https://content.illumidesk.com/lms/{version}/index.html"
    )
    template_html = template_response.text.replace(
        "</head>",
        """
            <script>
                var base_url = "{{ base_url }}";
                var url_prefix = "{{ url_prefix }}";
                var base_url_suffix = "{{ base_url_suffix }}";
            </script>
        </head>
        """,
    )
    # Hack(@gzuidhof): We need this until the index file in the bundle itself contains crossorigin (or crossorigin="anonymous") tags
    # we need to specify crossorigin assets specifically due to the COOP and COEP headers.
    return template_html.replace("<script ", "<script crossorigin ").replace(
        "<link ", "<link crossorigin "
    )


class LMSHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    @coop_coep_headers
    def get(self):
        html = (
            Environment(loader=BaseLoader)
            .from_string(
                get_template(
                    self.get_query_argument("lms_version", DEFAULT_LMS_VERSION)
                )
            )
            .render(
                url_prefix=self.url_prefix,
                base_url=self.base_url,
                base_url_suffix="/formgradernext",
                windows=(sys.prefix == "win32"),
                course_id=self.api.course_id,
                exchange=self.api.exchange,
                exchange_missing=self.api.exchange_missing,
            )
        )
        self.write(html)


handlers = [
    (r"/formgradernext.*", LMSHandler),
]


def rewrite(nbapp: NotebookApp, x: str) -> str:
    """Rewrites a path to remove the trailing slash.

    Args:
        nbapp (NotebookApp): a NotebookApp instance.
        x (str): the string that represents the path.

    Returns:
        str: the re written string.
    """
    web_app = nbapp.web_app
    pat = ujoin(web_app.settings["base_url"], x[0].lstrip("/"))
    return (pat,) + x[1:]


def load_jupyter_server_extension(nbapp: NotebookApp) -> None:
    nbapp.web_app.add_handlers(".*$", [rewrite(nbapp, x) for x in handlers])
