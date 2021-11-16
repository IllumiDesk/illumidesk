# Async nbgrader

A Jupyter Notebook server extension which adds:

- Async capabilities to `nbgrader`'s auto-grading service.
- Export grades as a CSV file for the `Canvas LMS`

## Installation

1. Clone this repo and install the pacakage with `pip`:

```bash
git clone https://github.com/illumidesk/async-nbgrader
cd async-nbgrader
pip install -e .
```

1. Create and activate your virtual environment:

```bash
virtualenv -p python3 venv
source venv/bin/activate
```

1. Install and Activate Extensions

Install and activate client and server extensions:

```bash
jupyter nbextension install --sys-prefix --py async_nbgrader --overwrite
jupyter nbextension enable --sys-prefix --py async_nbgrader
jupyter serverextension enable --sys-prefix --py async_nbgrader
```

## Run the Auto-Grader

This package leverages the same Python API available with `nbgrader`. Therefore no additional changes are required to run the auto-grader. For example, once you have collected assignments, run the following command to auto-grade assignments with the `async-nbgrader` server extension:

```bash
nbgrader autograde "<assignment-name>"
```

### Toggle to use the standard syncronous autograder

This package includes the option to set an environment variable to toggle whether to use the `asyncronous` version of the autograder or the `syncrononous` version (default is `async`):

| Environment Variable | Description | Default |
| --- | --- | --- |
| NBGRADER_ASYNC_MODE | Used to set whether the autograder runs syncronous or asyncronous mode | "true"  |

## Export Grades as a CSV

Follow the steps below to export grades from the `nbgrader` database to a `*.csv` (default is `canvas_grades.csv`) file:

1. Export the Canvas LMS grades as a CSV file from your Course's gradebook by following [these instructions](https://community.canvaslms.com/t5/Instructor-Guide/How-do-I-export-grades-in-the-Gradebook/ta-p/809).

1. Copy the CSV file to a location where the `ild` command has access to the exported CSV. (The `ild` command is used to export grades from the `nbgrader` database).

1. Run the `ild export` command to export grades from the `nbgrader` database:

```bash
ild export --canvas_import=/path/to/my/grades-from-canvas.csv --canvas_export=/path/to/my/grades-for-canvas.csv
```

By default, the `ild export` command uses the `canvas.csv` as the file to import grades from and the `canvas_grades.csv` to export grades to. You can override these values with the `--canvas_import` and the `--canvas_export` flags to designate the path and file name for the CSV file to import and export, respectively.

The `ild` command is a wrapper for the `nbgrader` command. Therefore all other flags included with the `nbgrader` CLI are available with the `ild` command, such as the `--debug` flag.

If successful, the output in the terminal should look similar to:

```bash
[ExportApp | WARNING] No nbgrader_config.py file found (rerun with --debug to see where nbgrader is looking)
[ExportApp | INFO] Using exporter: CanvasCsvExportPlugin
[ExportApp | INFO] Exporting grades to canvas_grades.csv
[ExportApp | INFO] Skipping second row
[ExportApp | INFO] Finding student with ID 358
[ExportApp | INFO] Finding submission of Student '358' for Assignment 'postgres-migration-test'
```

## Contributing

For general contribution guidelines, please refer to IllumiDesk's [contributing guidelines](https://github.com/IllumiDesk/illumidesk/blob/main/CONTRIBUTING.md).

The `async_nbgrader` package installs the `nbgrader` package as a required dependency, therefore you should not have to install it explicitly.

> The `async_nbgrader` package overrides `nbgrader`'s default auto-grading service (included with the `Formgrader` extension) by converting the grading service from a `syncronous` service to an `asyncronous` service. Thefore it's a good idea to get familiar with the `nbgrader` documentation (although not a must) to setup your local environment [by following these instructions](https://nbgrader.readthedocs.io/en/latest/contributor_guide/installation_developer.html).

Use `pytest` to run tests:

```bash
pytest -v
```

## License

Apache 2.0
