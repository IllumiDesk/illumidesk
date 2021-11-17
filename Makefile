.PHONY: help test

SHELL=/bin/bash

VENV_NAME?=venv
VENV_BIN=$(shell pwd)/${VENV_NAME}/bin
VENV_ACTIVATE=. ${VENV_BIN}/activate
OWNER?=illumidesk
PYTHON=${VENV_BIN}/python3

GRADERSERVICE_BASE_IMAGE=python
GRADERSERVICE_BASE_IMAGE_TAG=3.8
JUPYTERHUB_DOCKER_BASE_IMAGE=jupyterhub/jupyterhub
JUPYTERHUB_DOCKER_BASE_TAG=1.4.2
JUPYTERHUB_K8_BASE_IMAGE=jupyterhub/k8s-hub
JUPYTERHUB_K8_BASE_TAG=1.1.2

# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:
	@echo "illumidesk/illumidesk"
	@echo "====================="
	@echo
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## clean files from environment (cache, egg, etc)
	find . -name '*.pyc' -exec rm -f {} +
	rm -rf $(VENV_NAME) *.eggs *.egg-info dist build docs/_build .cache

dev: venv ## install the packages in editable mode
	${PYTHON} -m pip install -e src/async_nbgrader/.
	${PYTHON} -m pip install -e src/formgradernext/.
	${PYTHON} -m pip install -e src/graderservice/.
	${PYTHON} -m pip install -e src/illumidesk/.
	${PYTHON} -m pip install -e src/illumideskdummyauthenticator/.

build-grader-setup-service: ## build grader-setup-service docker image
	@docker build --build-arg BASE_IMAGE=${GRADERSERVICE_BASE_IMAGE}:${GRADERSERVICE_BASE_IMAGE_TAG} -t ${OWNER}/grader-setup-service:latest src/graderservice/. --no-cache

build-hubs-k8: ## build jupyterhub images kubernetes setups
	@docker build --build-arg BASE_IMAGE=${JUPYTERHUB_K8_BASE_IMAGE}:${JUPYTERHUB_K8_BASE_TAG} -t ${OWNER}/k8s-hub:base-${JUPYTERHUB_K8_BASE_TAG} src/illumidesk/. --no-cache
	@docker build --build-arg BASE_IMAGE=${OWNER}/k8s-hub:base-${JUPYTERHUB_K8_BASE_TAG} -t ${OWNER}/k8s-hub:${JUPYTERHUB_K8_BASE_TAG} src/illumideskdummyauthenticator/. --no-cache

build-hubs: ## build jupyterhub images for standard docker-compose and docker run setups
	@docker build --build-arg BASE_IMAGE=${JUPYTERHUB_DOCKER_BASE_IMAGE} -t ${OWNER}/jupyterhub:base-${JUPYTERHUB_DOCKER_BASE_TAG} src/illumidesk/. --no-cache
	@docker build --build-arg BASE_IMAGE=${OWNER}/jupyterhub:base-${JUPYTERHUB_DOCKER_BASE_TAG} -t ${OWNER}/jupyterhub:${JUPYTERHUB_DOCKER_BASE_TAG} src/illumideskdummyauthenticator/. --no-cache

pre-commit-all: ## run pre-commit hook on all files (mostly linting)
	${VENV_BIN}/pre-commit run --all-files || (printf "\n\n\n" && git --no-pager diff --color=always)

pre-commit-install: ## set up the git hook scripts
	${VENV_BIN}/pre-commit --version
	${VENV_BIN}/pre-commit install

prepare: ## install virtualenv and create virtualenv with the venv folder
	which virtualenv || python3 -m pip install virtualenv

push-all: ## push jupyterhub images to docker hub
	@docker push ${OWNER}/grader-setup-service:latest
	@docker push ${OWNER}/jupyterhub:${JUPYTERHUB_DOCKER_BASE_TAG}
	@docker push ${OWNER}/k8s-hub:${JUPYTERHUB_DOCKER_K8_TAG}

test: dev ## run tests for all packages
	${VENV_BIN}/pytest -v src/async_nbgrader
	${VENV_BIN}/pytest -v src/formgradernext/tests
	${VENV_BIN}/pytest -v src/graderservice
	${VENV_BIN}/pytest -v src/illumidesk
	${VENV_BIN}/pytest -v src/illumideskdummyauthenticator

test-create-cov: ## create coverage report
	${VENV_BIN}/pytest --cov=async_nbgrader src/async_nbgrader/async_nbgrader/tests
	${VENV_BIN}/pytest --cov=formgradernext src/formgradernext/tests
	${VENV_BIN}/pytest --cov=graderservice src/graderservice/tests
	${VENV_BIN}/pytest --cov=illumidesk src/illumidesk/tests
	${VENV_BIN}/pytest --cov=illumideskdummyauthenticator src/illumideskdummyauthenticator/tests

test-push-cov: ## push coverage report to codecov
	@bash <(curl -s https://codecov.io/bash)

venv: prepare ## create virtual environment
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install -r dev-requirements.txt
	make pre-commit-install