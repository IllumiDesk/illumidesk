#!/bin/bash

set -o errexit

# free up port 5432
stop_postgres () {
  echo "Stopping Travis Postgres service"
  sudo service postgresql stop
}

setup_dependencies() {
  echo "INFO:
  Setting up dependencies.
  "
  sudo apt update -y && \
    sudo apt install realpath \
                python \
                python-pip -y && \
    sudo apt install --only-upgrade docker-ce -y

  docker info
}

main() {
  stop_postgres
  setup_dependencies
}

main