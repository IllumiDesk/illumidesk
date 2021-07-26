.PHONY: all prepare venv lint test clean

SHELL=/bin/bash

VENV_NAME?=venv
VENV_BIN=$(shell pwd)/${VENV_NAME}/bin
VENV_ACTIVATE=. ${VENV_BIN}/activate

PYTHON=${VENV_BIN}/python3

TEST?=bar

all:
	@echo "make deploy"
	@echo "    Run deployment scripts."
	@echo "make prepare"
	@echo "    Create python virtual environment and install dependencies."
	@echo "make lint"
	@echo "    Run lint and formatting on project."
	@echo "make test"
	@echo "    Run tests on project."
	@echo "make clean"
	@echo "    Remove python artifacts and virtualenv."

prepare:
	which virtualenv || python3 -m pip install virtualenv
	make venv

venv:
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install -r dev-requirements.txt

dev: venv
	${PYTHON} -m pip install -e src/illumidesk/.
	${PYTHON} -m pip install -e src/graderservice/.

lint: venv
	${VENV_BIN}/flake8 src
	${VENV_BIN}/black .

clean:
	find . -name '*.pyc' -exec rm -f {} +
	rm -rf $(VENV_NAME) *.eggs *.egg-info dist build docs/_build .cache

test: dev
	${VENV_BIN}/pytest -v src/illumidesk
	${VENV_BIN}/pytest -v src/graderservice

build-hubs-k8:
	@docker build --build-arg BASE_IMAGE=jupyterhub/k8s-hub:0.11.1-n495.h232e257c -t illumidesk/k8s-hub:1.4.1 src/illumidesk/. --no-cache
	@docker build --build-arg BASE_IMAGE=illumidesk/k8s-hub:1.4.1 -t illumidesk/k8s-hub:dummy-auth-1.4.1 src/illumideskdummyauthenticator/. --no-cache

build-hubs:
	@docker build --build-arg BASE_IMAGE=jupyterhub/jupyterhub:1.4.1 -t illumidesk/jupyterhub:1.4.1 src/illumidesk/. --no-cache
	@docker build --build-arg BASE_IMAGE=illumidesk/jupyterhub:1.4.1 -t illumidesk/jupyterhub:dummy-auth-1.4.1 src/illumideskdummyauthenticator/. --no-cache
