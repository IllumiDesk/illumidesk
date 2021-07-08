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

Follow the steps below to test the IllumiDesk setup with the `IllumiDeskDummyAuthenticator`:

1. Ensure that `JupyterHub.authenticator_class = IllumiDeskDummyAuthenticator` is set in the `jupyterhub_config.py`.
1. Start the JupyterHub with `jupyterhub --config=/path/to/my/jupyterhub_config.py`
1. Navigate to `http://127.0.0.1:8000/hub/login`.
1. Add form values and submit to login.

You may also use the provided `Dockerfile` to build a docker image:

1. Build the docker image with `docker build -t illumidesk/jupyterhub:latest . --no-cache`.
1. Run the docker container with `docker run -d -p 8000:8000 illumidesk/jupyterhub:latest .`.
1. Navigate to `http://127.0.0.1:8000/hub/login`.
1. Add form values and submit to login.

> **NOTE**: when using docker your IPv4 address may not work with localhost.
