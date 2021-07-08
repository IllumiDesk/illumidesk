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

## Dev Setup

Follow the steps below to test the IllumiDesk setup with the `IllumiDeskDummyAuthenticator` with a `virtualenv` or with a `docker` container.

Follow the `CONTRIBUTING.md` guide in the root of this repo to install all required dependencies.

### Virtualenv

1. Create and activate your virtual environment:

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -e .
```

2. Export the `JUPYTERHUB_CRYPT_KEY` with `export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)`.
3. Ensure that `JupyterHub.authenticator_class = IllumiDeskDummyAuthenticator` is set in the `jupyterhub_config.py`.
4. Start the JupyterHub with `jupyterhub --config=/path/to/my/jupyterhub_config.py`
5. Navigate to `http://127.0.0.1:8000/hub/login`.
6. Add form values and submit to login.

### Docker

You may also use the provided `Dockerfile` to build a docker image:

1. Create a value for the `JUPYTERHUB_CRYPT_KEY` environment variable: `openssl rand -hex 32`
2. Build the docker image with `docker build -t illumidesk/jupyterhub:latest . --no-cache`.
3. Run the docker container:

```bash
docker run -d \
  -p 8000:8000 \
  -e illumidesk/jupyterhub:latest .
```

4. Navigate to `http://127.0.0.1:8000/hub/login`.
5. Add form values and submit to login.

> **NOTE**: when using docker your IPv4 address may not work with localhost.
