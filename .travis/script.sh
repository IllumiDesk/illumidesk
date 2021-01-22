#!/bin/bash

set -e

run_linters () {
  echo "Running linters ..."
  flake8 src/
  black --check src/
}

run_unit_tests () {
  echo "Running unit tests ..."
  python3 -m pytest
}

run_coverage_report () {
  echo "Running coverage report ..."
  pytest --cov=illumidesk src/illumidesk/tests
}

main () {
    # linting errors shouldn't make travis fail
    set +e
    run_linters
    set -e
    run_unit_tests
    run_coverage_report
}

main