#!/bin/bash

set -e

upload_codecov () {
  echo "Upload codecov ..."
  bash <(curl -s https://codecov.io/bash)
}

main() {
  upload_codecov
}

main