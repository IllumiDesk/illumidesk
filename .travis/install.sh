#!/bin/bash

set -o errexit

install_node_requirements () {
  echo "Install node requirements ..."
  npx semantic-release
}

install_python_requirements () {
  echo "Install python requirements ..."
  python3 -m pip install -r dev-requirements.txt
}

install_illumidesk_package () {
  echo "Install illumidesk package ..."
  python3 -m pip install -r src/illumidesk/requirements.txt
}

main() {
  install_python_requirements
  install_illumidesk_package
}

main
