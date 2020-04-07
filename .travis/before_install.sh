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

# upgrade docker-compose to a more recent version so we can use it for
# testing
update_compose () {
  echo "Upgrade docker-compose"
  sudo rm /usr/local/bin/docker-compose
  curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m) > docker-compose
  chmod +x docker-compose
  sudo mv docker-compose /usr/local/bin
  docker-compose --version
}

update_docker_configuration() {
  echo "INFO:
  Updating docker configuration
  "

  echo '{
  "experimental": true,
  "storage-driver": "overlay2",
  "max-concurrent-downloads": 50,
  "max-concurrent-uploads": 50
}' | sudo tee /etc/docker/daemon.json
  sudo service docker restart
}

main() {
  stop_postgres
  setup_dependencies
  update_compose
  update_docker_configuration
}

main