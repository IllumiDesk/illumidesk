# IllumiDesk Dummy Authenticator

## Overview

This package provides users with a JupyterHub compatible authenticator used for testing LTI 1.x compatible
authentication dictionaries. Use cases include local dev testing and testing end-to-end workflows without relying on
LTI 1.x login flows.

The `graderservice` microservice included in this repo configures the user's environment when logging into the system. A convinience class, `IllumiDeskDummyAuthenticator`, replicates how the LTI 1.x authenticators return the authentication dictionary:

- `username`
- `auth_state[assignment_name]`
- `auth_state[course_id]`
- `auth_state[lms_user_id]`
- `auth_state[user_role]`

> **NOTE**: the `graderservice` _only_ supports deployments running with `Kubernetes`. Therefore the `jupyterhub_config.py` file in the `src/illumideskdummyauthenticator` folder does not assign the `post_auth_hook` to the `setup_course_hook`. Refer to the [`Kubernetes`](#kubernetes) section below for an example of how to configure the `post_auth_hook` with the `setup_course_hook` included with the `illumidesk` package.

## Dev Setup

Follow the steps below to test the IllumiDesk setup with the `IllumiDeskDummyAuthenticator` with a `virtualenv`, with a stand alone `docker` container, or with `kubernetes`.

Follow the `CONTRIBUTING.md` guide in the root of this repo to install all required dependencies.

### Virtualenv

1. Create and activate your virtual environment:

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -e ../illumidesk/.
pip install -e .
```

2. Export the `JUPYTERHUB_CRYPT_KEY` with `export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)`.
3. Ensure that `JupyterHub.authenticator_class = IllumiDeskDummyAuthenticator` is set in the `jupyterhub_config.py`.
4. Start the JupyterHub with `jupyterhub --config=/path/to/my/jupyterhub_config.py`.
5. Navigate to `http://127.0.0.1:8000/hub/login`.
6. Add form values and submit to login.

### Docker

Use the provided `Dockerfile` to build a docker image using the `illumidesk/jupyterhub:<tag>` image.

1. Create a value for the `JUPYTERHUB_CRYPT_KEY` environment variable: `openssl rand -hex 32`
2. Build the docker image with `docker build -t illumidesk/jupyterhub:<tag> . --no-cache`.
3. Run the docker container:

```bash
docker run -d \
  -p 8000:8000 \
  -e illumidesk/jupyterhub:latest .
```

4. Navigate to `http://127.0.0.1:8000/hub/dummy/login`.
5. Add form values and submit to login.

> **NOTE**: when using docker your IPv4 address may not work with localhost.

### Kubernetes

1. You may also use the provided `Dockerfile` to build a docker image built to run with a `Kubernetes` cluster. The provided Dockerfile does not provide a Kubernetes-compatible base image. However, you can use the `--build-args` option to specify the image's base image:

```bash
docker build \
  --build-arg BASE_IMAGE=illumidesk/k8s-hub:1.1.1 \
  -t illumidesk/jupyterhub:test . \
  --no-cache
```

2. Create a value for the `JUPYTERHUB_CRYPT_KEY` environment variable: `openssl rand -hex 32`
3. Configure the `illumidesk/illumidesk` [helm chart](https://github.com/illumidesk/helm-chart) to set the `authenticator_class` and the `post_auth_hook` mentioned above.
4. Deploy the `illumidesk/illumidesk` application to a `kubernetes` cluster. [Refer to IllumiDesk's helm-chart repo](https://github.com/illumidesk/helm-chart) for further instructions.
5. Navigate to `https://<external-facing-address>/hub/login`.

> **NOTE**: when using docker your IPv4 address may not work with localhost.