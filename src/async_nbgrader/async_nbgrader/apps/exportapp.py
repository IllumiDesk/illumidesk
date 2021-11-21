# coding: utf-8

from nbgrader.api import Gradebook
from nbgrader.apps import ExportApp as BaseExportApp
from traitlets import Instance
from traitlets import Type
from traitlets import default

from ..plugins import CanvasCsvExportPlugin
from ..plugins import CustomExportPlugin

aliases = {
    "log-level": "Application.log_level",
    "db": "CourseDirectory.db_url",
    "to": "CanvasCsvExportPlugin.to",
    "canvas_import": "CanvasCsvExportPlugin.canvas_import",
    "exporter": "ExportApp.plugin_class",
    "assignment": "CanvasCsvExportPlugin.assignment",
    "student": "CanvasCsvExportPlugin.student",
    "course": "CourseDirectory.course_id",
}

flags = {}


class ExportApp(BaseExportApp):
    """Custom nbgrader export app to export grades from a Canvas LMS
    course.
    """

    name = "async_nbgrader-export"

    aliases = aliases

    plugin_class = Type(
        CanvasCsvExportPlugin,
        klass=CustomExportPlugin,
        help="The plugin class for exporting the grades.",
    ).tag(config=True)

    plugin_inst = Instance(CustomExportPlugin).tag(config=False)

    @default("classes")
    def _classes_default(self):
        classes = super(ExportApp, self)._classes_default()
        classes.append(ExportApp)
        classes.append(CustomExportPlugin)
        return classes

    def start(self):
        super(ExportApp, self).start()
        self.init_plugin()
        with Gradebook(self.coursedir.db_url, self.coursedir.course_id) as gb:
            self.plugin_inst.export(gb)
