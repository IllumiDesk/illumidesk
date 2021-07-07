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
