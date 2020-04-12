  
#!/bin/bash

set -o errexit

install_requirements () {
  echo "Install requirements ..."
  python3 -m pip install -r dev-requirements.txt
}

install_illumidesk_package () {
  echo "Install illumidesk package ..."
  python3 -m pip install -e src/.
}

main() {
  install_requirements
  install_illumidesk_package
}

main