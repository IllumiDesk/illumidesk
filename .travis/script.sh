#!/bin/bash

set -e

run_linters () {
  echo "Running linters ..."
  flake8 src/
  ansible-lint
}

run_unit_tests () {
  echo "Running unit tests ..."
  python3 -m pytest
}

main () {
    # linting errors shouldn't make travis fail
    set +e
    run_linters
    set -e
    echo "Running unit tests..."
    run_unit_tests
}

main