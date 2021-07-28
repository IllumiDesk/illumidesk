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

## Environment Variables

| Environment Variable | Description | Type | Default Value |
| --- | --- | --- | --- |
| JUPYTERHUB_API_TOKEN | The shared grader notebook image:tag | `string` | `illumidesk/grader-notebook:latest` |
| JUPYTERHUB_API_URL | The JupyterHub internal API URL | `string` | `http://hub:8081/hub/api` |
| ORGANIZATION_NAME | The organization name that represents the root tenant name | `string` | `"my-org"` |
| ILLUMIDESK_MNT_ROOT | The IllumiDesk root for the organization  | `string` | `/illumidesk-courses` |
| LTI13_AUTHORIZE_URL | The OIDC/LTI 1.3 authorization URL | `string` | `""` |
| LTI13_PRIVATE_KEY | The private key's path used to create JWKS keys used with LTI 1.3 | `string` | `""` |
| POSTGRES_NBGRADER_HOST | The nbgrader Postgres host endpoint | `string` | `""` |
| POSTGRES_NBGRADER_PORT | The nbgrader Postgres port | `string` | `5432` |
| POSTGRES_NBGRADER_USER | The nbgrader Postgres username | `string` | `"` |
| POSTGRES_NBGRADER_PASSWORD | The nbgrader Postgres username | `string` | `""` |
| SETUP_COURSE_SERVICE_NAME | The setup course service name | `string` | `grader-setup-service` |
| SETUP_COURSE_SERVICE_PORT | The setup cours service port | `string` | `8000` |
| NB_GRADER_UID | The grader's home directory user id  | `string` | `10001` |
| NB_GRADER_GID | The grader's home directory group id | `string` | `100` |


## License

Apache 2.0
