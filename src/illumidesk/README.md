# IllumiDesk Custom JupyterHub LTI Authenticators

## Overview

- JupyterHub compatible Authenticators
- JupyterHub REST API client

## Dev Install

1. Follow the steps in the `CONTRIBUTION.md` guide in the root of this repo to install all dependencies.

1. Install in editable mode:

```bash
virtualenv -p python3 venv
source venv/bin/activate
python3 -m pip install -e .
```

2. Start the JupyterHub in your local environment:

```bash
jupyterhub --config=jupyterhub_config.py
```

Once the JupyterHub server is running navigate to `http://<your-ipv4-address>:8000/hub/login`.

## Test with the IllumIDeskDummyAuthenticator

This repo includes the `graderservice` microservice that configures the user's environment when logging into the system with the LTI 1.x standard. A convinience class, `IllumiDeskDummyAuthenticator`, replicates how the LTI 1.x authenticators return the authentication dictionary:

- `username`
- `auth_state[assignment_name]`
- `auth_state[course_id]`
- `auth_state[lms_user_id]`
- `auth_state[user_role]`

Follow the steps below to test the IllumiDesk setup with the `IllumiDeskDummyAuthenticator`:

1. Ensure that `JupyterHub.authenticator_class = IllumiDeskDummyAuthenticator` is set in the `jupyterhub_config.py`.
1. Start the JupyterHub with `jupyterhub --config=jupyterhub_config.py`
1. Navigate to `http://127.0.0.1:8000/hub/login`.
1. Add form values and submit to login.

You may also use the provided `Dockerfile` to build a docker image:

1. Build the docker image with `docker build -t illumidesk/jupyterhub:latest . --no-cache`.
1. Run the docker container with `docker run -d -p 8000:8000 illumidesk/jupyterhub:latest`.
1. Navigate to `http://127.0.0.1:8000/hub/login`.
1. Add form values and submit to login.

> **NOTE**: when using docker your IPv4 address may not work with localhost.

