import csv

from nbgrader.api import Gradebook
from nbgrader.api import MissingEntry
from nbgrader.plugins import BasePlugin
from traitlets import Unicode


class CustomExportPlugin(BasePlugin):
    """Custom nbgrader export plugin that exports grades from
    the nbgrader database to the Canvas LMS CSV format.
    """

    canvas_export = Unicode(
        "",
        help="The destination path and file name for the Canvas LMS course's grades.",
    ).tag(config=True)

    canvas_import = Unicode(
        "",
        help="The source path and file name of grades exported from the Canvas LMS course.",
    ).tag(config=True)


class CanvasCsvExportPlugin(CustomExportPlugin):
    """Canvas CSV exporter plugin."""

    def export(self, gradebook: Gradebook) -> None:
        """Creates a CSV file from nbgrader's gradebook.

        Args:
            gradebook (Gradebook): an nbgrader gradebook instance.
        """
        if self.canvas_export == "":
            dest = "canvas_grades.csv"
        else:
            dest = self.to

        if self.canvas_import == "":
            canvas_import = "canvas.csv"
        else:
            canvas_import = self.canvas_import

        self.log.info("Exporting grades to %s", dest)

        with open(canvas_import, "r") as csv_file, open(dest, "w") as op_csv_file:
            csv_reader = csv.DictReader(csv_file)
            fields = csv_reader.fieldnames
            csv_writer = csv.DictWriter(op_csv_file, fields)
            csv_writer.writeheader()
            for row in csv_reader:
                if "Points Possible" in row["Student"]:
                    self.log.info("Skipping second row")
                    csv_writer.writerow(row)
                    continue
                self.log.info("Finding student with ID %s", row["ID"])
                for column in fields:
                    if " (" not in column:
                        continue
                    assignment_name = column.split(" (")[0]
                    self.log.info(
                        "Finding submission of Student '%s' for Assignment '%s'",
                        row["ID"],
                        assignment_name,
                    )
                    submission = None
                    try:
                        submission = gradebook.find_submission(
                            assignment_name, row["ID"]
                        )
                        row[column] = max(
                            0.0, submission.score - submission.late_submission_penalty
                        )
                    except MissingEntry:
                        self.log.info(
                            "Submission of Student '%s' for Assignment '%s' not found",
                            row["ID"],
                            assignment_name,
                        )
                        continue
                csv_writer.writerow(row)
