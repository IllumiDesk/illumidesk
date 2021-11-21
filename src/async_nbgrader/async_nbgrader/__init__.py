"""Tornado handlers for nbgrader background service."""
from .handlers import load_jupyter_server_extension  # noqa: F401


def _jupyter_nbextension_paths():
    return []


def _jupyter_server_extension_paths():
    return [
        dict(module="async_nbgrader"),
    ]
