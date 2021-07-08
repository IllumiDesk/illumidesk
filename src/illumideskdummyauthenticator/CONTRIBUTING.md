## Setting up a development environment

### Install requirements

Follow the steps in the CONTRIBUTING.md guide in the root of this repo to install development dependencies and to ensure you have an understanding of the development and contribution processes.

Then install the package in editable mode:

```
$ pip install -e .
```

### Running your local project

For developing the `IllumiDeskDummyAuthenticator`, you should create a `jupyterhub_config.py` file with:

- A simple spawner
- The `IllumiDeskDummyAuthenticator` as the default authenticator
- Enable the authentication state

For example:

```python
# jupyterhub_config.py

c.JupyterHub.spawner_class = 'simplespawner.SimpleLocalProcessSpawner'
c.JupyterHub.authenticator_class = 'illumidesk.IllumiDeskDummyAuthenticator'
c.Authenticator.enable_auth_state = True
c.Authenticator.admin_users = {'admin'}
```

Before starting the `JupyterHub` you will need to set the `JUPYTERHUB_CRYPT_KEY` environment variable to encrypt the authentication dictionary. Use the following command to set the `JUPYTERHUB_CRYPT_KEY`:

```bash
export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)
```

*Please do not use the `IllumIDeskDummyAuthenticator` or the `SimpleLocalProcessSpawner` in production!*.

Then you can run locally by using:

```
jupyterhub -f ~/jupyterhub_config.py
```

### Runing tests

On the project folder you can run tests by using pytest

```
$ pytest -v
```
