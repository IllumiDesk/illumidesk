import os
from string import Template

from jinja2 import ChoiceLoader
from jinja2 import FileSystemLoader
from jupyterhub.handlers import BaseHandler
from tornado.escape import url_escape
from tornado.httputil import url_concat

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


class LocalBase(BaseHandler):
    """Custom BaseHandler to facilitate templates management.

    Ref: https://github.com/jupyterhub/nativeauthenticator
    """

    _template_dir_registered = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not LocalBase._template_dir_registered:
            self.log.debug("Adding %s to template path", TEMPLATE_DIR)
            loader = FileSystemLoader([TEMPLATE_DIR])
            env = self.settings["jinja2_env"]
            previous_loader = env.loader
            env.loader = ChoiceLoader([previous_loader, loader])
            LocalBase._template_dir_registered = True


class IllumiDeskDummyLoginHandler(LocalBase):
    """Render the login page for the IllumiDeskDummyAuthenticator."""

    def _render(self, login_error=None, username=None):
        context = {
            "next": url_escape(self.get_argument("next", default="")),
            "username": username,
            "login_error": login_error,
            "login_url": self.settings["login_url"],
            "authenticator_login_url": url_concat(
                self.authenticator.login_url(self.hub.base_url),
                {"next": self.get_argument("next", "")},
            ),
        }
        custom_html = Template(
            self.authenticator.get_custom_html(self.hub.base_url)
        ).render(**context)
        return self.render_template(
            "dummy_login.html",
            **context,
            custom_html=custom_html,
        )

    async def get(self):
        """Display custom page"""
        html = await self.render_template(
            "dummy_login.html",
        )
        self.finish(html)

    # async def post(self):
    #     """Handle the request data when sent with the login form."""
    #     user_info = {
    #         "username": self.get_body_argument("username", strip=False),
    #         "assignment_name": self.get_body_argument("assignment_name", strip=False),
    #         "course_id": self.get_body_argument("course_id", "", strip=False),
    #         "lms_user_id": bool(self.get_body_argument("lms_user_id", "", strip=False)),
    #         "user_role": bool(self.get_body_argument("user_role", "", strip=False)),
    #     }

    #     html = await self.render_template(
    #         "dummy_login.html",
    #     )
    #     self.finish(html)
