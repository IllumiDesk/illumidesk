import contextlib
import os
from typing import Dict

from jupyter_core.paths import jupyter_config_path
from nbgrader.apps import NbGrader
from nbgrader.apps.api import NbGraderAPI
from nbgrader.auth import Authenticator
from nbgrader.coursedir import CourseDirectory
from nbgrader.exchange import ExchangeList


@contextlib.contextmanager
def chdir(dirname: str) -> None:
    """Utility function to change directories.

    Args:
        dirname (str): the directory name to change into.
    """
    currdir = os.getcwd()
    os.chdir(dirname)
    yield
    os.chdir(currdir)


@contextlib.contextmanager
def get_assignment_dir_config(notebook_dir: str) -> Dict[str, Dict[str, str]]:
    """[summary]

    Args:
        notebook_dir (str): The assignment directory configuration.

    Returns:
        Dict[str, Dict[str, str]]: the application configuration.
    """
    # first get the exchange assignment directory
    with chdir(notebook_dir):
        config = load_config()

    lister = ExchangeList(config=config)
    assignment_dir = lister.assignment_dir

    if assignment_dir == ".":
        assignment_dir = notebook_dir + "/.jupyter"

    # now cd to the full assignment directory and load the config again
    with chdir(assignment_dir):
        app = NbGrader()
        app.config_file_paths.append(os.getcwd())
        app.load_config_file()

        yield app.config


def load_config() -> Dict[str, Dict[str, str]]:
    """Method to load the application's configuration.

    Returns:
        Iterator[Dict[str, Dict[str, str]]]: The application configuration.
    """
    paths = jupyter_config_path()
    paths.insert(0, os.getcwd())

    app = NbGrader()
    app.config_file_paths.append(paths)
    app.load_config_file()

    return app.config


def get_nbgrader_api(notebook_dir: str, course_id: str = None) -> NbGraderAPI:
    """Returns an instance of the NbraderAPI based on the notebook directory and
    course_id.

    Args:
        notebook_dir ([str]): the notebook directory path and filename.
        course_id ([str], optional): The course _id, defaults to None.

    Returns:
        NbGraderAPI: and instance of the nbrader API.
    """
    with get_assignment_dir_config(notebook_dir) as config:
        if course_id:
            config.CourseDirectory.course_id = course_id

        coursedir = CourseDirectory(config=config)
        authenticator = Authenticator(config=config)
        api = NbGraderAPI(coursedir, authenticator)
        return api
