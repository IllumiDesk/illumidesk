import os
import subprocess as sp
import sys
import logging

from six import StringIO
from jupyter_core.application import NoStart

from ..apps.async_nbgraderapp import AsyncNbGraderApp
from nbgrader.validator import Validator


def run_async_nbgrader(args, retcode=0, env=None, stdout=False):
    # store os.environ
    old_env = os.environ.copy()
    if env:
        os.environ = env

    # create the application
    app = AsyncNbGraderApp.instance()

    # hook up buffers for getting log output or stdout/stderr
    if not stdout:
        log_buff = StringIO()
    else:
        stdout_buff = StringIO()
        orig_stdout = sys.stdout
        sys.stdout = stdout_buff
        Validator.stream = stdout_buff

    try:
        app.initialize(args)
        if not stdout:
            app.init_logging(logging.StreamHandler, [log_buff], color=False, subapps=True)
        app.start()
    except NoStart:
        true_retcode = 0
    except SystemExit as e:
        true_retcode = e.code
    else:
        true_retcode = 0
    finally:
        # get output
        if not stdout:
            out = log_buff.getvalue()
            log_buff.close()
        else:
            out = stdout_buff.getvalue()
            stdout_buff.close()
            sys.stdout = orig_stdout
            Validator.stream = orig_stdout

        # reset application state
        app.reset()

        # restore os.environ
        os.environ = old_env

    if retcode != true_retcode:
        raise AssertionError(
            "process returned an unexpected return code: {}".format(true_retcode))

    return out
