#!/bin/bash

set -o errexit

# free up port 5432
install_requirements () {
  echo "Install requirements ..."
  python3 -m pip install -r dev-requirements.txt
}

main() {
  install_requirements
}

main