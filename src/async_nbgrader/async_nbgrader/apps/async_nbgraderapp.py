#!/usr/bin/env python
# coding: utf-8

from textwrap import dedent

from nbgrader.apps import NbGraderApp

from .exportapp import ExportApp
from .processmessageapp import ProcessMessageApp


class AsyncNbGraderApp(NbGraderApp):
    """Custom nbgrader application to provide async capabilities to nbgrader's
    autograder.
    """

    name = "async_nbgrader-autograder"

    subcommands = dict(
        export=(
            ExportApp,
            dedent(
                """
                Export grades from the database to another format.
                """
            ).strip(),
        ),
        process_message=(
            ProcessMessageApp,
            dedent(
                """
                Handles base64 encoded messages
                """
            ).strip(),
        ),
    )


def main():
    AsyncNbGraderApp.launch_instance()
