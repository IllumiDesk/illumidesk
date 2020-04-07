[![Build Status](https://travis-ci.com/IllumiDesk/illumidesk.svg?branch=master)](https://travis-ci.com/IllumiDesk/illumidesk)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Code style black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# IllumiDesk

## Overview

JupyterHub + docker + nbgrader

## Prerequisites

On remote host:

- Tested with Ubuntu 18.04

On machine running `ansible-playbook`:

- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

## Quick Start

### Initial Server Setup

> `Note`: depending on your server's resource the ansible script can take anywhere between 5/10 minutes. Most of this time is spent building the images themselves as they are not stored in a docker registry.

1. Create a `ansible/hosts` file from the provided `ansible/hosts.example`:

    cp `ansible/hosts.example` `ansible/hosts`

2. Update `private_key_file` in the `hosts` file with the PEM key to access VM instance.

3. Update `ansible_ssh_host` with your instance's IPv4 address.

4. Change into the ansible directory:

    cd ansible

5. Run `ansible-playbook` using the flags below:

- Remote server SSH private key: `--private-key`
- Remote user: `-u`

For example:

```bash
ansible-playbook \
  provisioning.yml \
  --private-key /path/to/server/private/key \
  -u ubuntu \
  --extra-vars \
  "org_name_param=my-edu"
  -v
```

- Extra variables: `--extra-vars`
  - Organization name: `org_name`

You may add any of the variables listed in `ansible/group_vars/all.yml` when running the playbook.

6. Once the ansible playbook has finished running the JupyterHub should be available at:

    `http://<public_ipv4>:8000/`

7. Login with either the instructor or student accounts:

- **Instructor Role**: instructor1
- **Student Role**: student1

### Initial Course Setup

By default, this setup uses the `FirstUseAuthenticator` and as such accepts any password you designate when first logging into the system.

1. Log in with the instructor account which by default is `instructor1`

2. Access the shared grader notebook accessible by clicking on `Control Panel --> Services --> Course ID` (intro101 by default)

3. Open a Jupyter terminal by clicking on `New --> Terminal`.

4. Type `nbgrader quickstart intro101 --force`

5. Click on the `Grader Console` tab and follow the steps available within the nbgrader docs to generate and release assignments for the students.

## Components

* **JupyterHub**: Runs [JupyterHub](https://jupyterhub.readthedocs.org/en/latest/getting-started.html#overview) within a Docker container running as root.

* **Authenticator**: Authentication service. This setup relies on the [FirstUseAuthenticator](https://github.com/jupyterhub/firstuseauthenticator).

* **Spawner**: Spawning service to manage user notebooks. This setup uses [DockerSpawner](https://github.com/jupyterhub/dockerspawner).

* **Data Directories**: This repo uses `docker-compose` to start all services and data volumes for JupyterHub, notebook directories, databases, and the `nbgrader exchange` directory using mounts from the host's file system.

* **Databases**: This setup relies on a standard `Postgres` database running in its own container.

* **Network**: An external bridge network named `jupyter-network` is used by default. The grader service and the user notebooks are attached to this network.

## Customization

### LTI Authenticator

Open the JupyterHub configuration file located in `ansible/roles/jupyterhub/files/jupyterhub_config.py`. Change the `JupyterHub.uthenticator_class` from `firstuseauthenticator.FirstUseAuthenticator` to `LTI11Authenticator`. For example:

Default authenticator setting:

```python
c.JupyterHub.authenticator_class = 'firstuseauthenticator.FirstUseAuthenticator'
```

LTI 1.1 authenticator:

```python
c.JupyterHub.authenticator_class = LTI11Authenticator
```

By default the consumer key is `my_consumer_key` and the shared secret is `my_shared_secret`. If you would like to change these values, update the `LTIAuthenticator.consumers` dictionary within the `jupyterhub_config.py` file.

Then, rerun the ansible playbook to update your system's settings.

### Configuration Files

The configuration changes depending on how you decide to update this setup. Essentially customizations boil down to:

1. JupyterHub configuration using `jupyterhub_config.py`:

    - Authenticators
    - Spawners
    - Services

> **Note**: By default the `jupyterhub_config.py` file is located in `/etc/jupyter/jupyterhub_config.py` within the running JupyterHub container, however, if you change this location (which would require an update to the JupyterHub's Dockerfile) then you need to make sure you are using the correct configuration file with the `jupyterhub -f /path/to/jupyterhub_config.py` option.

Whenever possible we try to adhere to [JupyterHub's](https://jupyterhub.readthedocs.io/en/stable/installation-basics.html#folders-and-file-locations) recommended paths:

- `/srv/jupyterhub` for all security and runtime files
- `/etc/jupyterhub` for all configuration files
- `/var/log` for log files

2. Nbgrader configurations using `nbgrader_config.py`.

Three `nbgrader_config.py` files should exist:

**Grader Account**

* **Grader's home: `/home/grader-{course_id}/.jupyter/nbgrader_config.py`**: defines how `nbgrader` authenticates with a third party service. This setup uses the `JupyterHubAuthPlugin`, the log file's location, and the `course_id` the grader account manages.
* **Grader's course: `/home/grader-{course_id}/{course_id}/nbgrader_config.py`**: configurations related to how the course files themselves are managed, such as solution delimeters, code stubs, etc.

**Instructor/Learner Account**

* **Instructor/Learner settings `/etc/jupyter/nbgrader_config.py`**: defines how `nbgrader` authenticates with a third party service, such as `JupyterHub` using the `JupyterHubAuthPlugin`, the log file's location, etc. Instructor and learner accounts do **NOT** contain the `course_id` identifier in their nbgrader configuration files.

3. Jupyter Notebook configuration using `jupyter_notebook_config.py`. This configuration is standard fare and unless required does not need customized edits.

4. For this setup, the deployment configuration is defined primarily with `docker-compose.yml`.

### Build the Stack

The following docker images are created/pulled with this setup:

- JupyterHub image
- Postgres image
- Reverse-proxy image
- Jupyter Notebook Student image
- Jupyter Notebook Instructor image
- Jupyter Notebook shared Grader image

When building the images the configuration files are copied to the image from the host using the `COPY` command. Environment variables are stored in `env.*` files. You can either customize the environment variables within the `env.*` files or add new ones as needed. The `env.*` files are used by docker-compose to reduce the file's verbosity.

### Spawner

By default this setup includes the `IllumiDeskDockerSpawner` class which extends the `DockerSpawner` class. This implementation calls the `authenticator` function to get a list of the user's keys/values and uses the `pre_spawn_hook` to set the user's image based on user role.

Edit the `JupyterHub.spawner_class` to update the spawner used by JupyterHub when launching user containers. For example, if you are changing the spawner from `DockerSpawner` to `KubeSpawner`:

Before:

```python
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
```

After:

```python
c.JupyterHub.spawner_class = 'kubespawner.KubeSpawner'
```

As mentioned in the [authenticator](#authenticator) section, make sure you refer to the spawner's documentation to consider all settings before launching JupyterHub.

### Proxies

There are two types of proxies that work with JupyterHub:

- JupyterHub's proxy
- Externally managed reverse-proxy

JupyterHub's proxy manages routing and optionally TSL termination. Reverse-proxies help manage multiple services with one domain, including JupyterHub.

This setup uses JupyterHub's [configurable-http-proxy]((https://github.com/jupyterhub/configurable-http-proxy)) running in a separate container which enables JupyterHub restarts without interrupting active sessions between end-users and their Jupyter Notebooks.

> **Warning**: CHP is **not** setup with TSL. Refer to [CHP's official documentation](https://github.com/jupyterhub/configurable-http-proxy) to set up TSL termination.

### Jupyter Notebook Images

**Requirements**

- The Jupyter Notebook image needs to have `JupyterHub` installed and this version of JupyterHub **must coincide with the version of JupyterHub that is spawing the Jupyter Notebook**. By default the `jupyter/docker-stacks` images have JupyterHub installed.
- Use one of images provided by the [`jupyter/docker-stacks`](https://github.com/jupyter/docker-stacks) images as the base image.
- Make sure the image is on the host used by the spawner to launch the user's Jupyter Notebook.

There are three notebook images:

- [Student](roles/common/templates/Dockerfile.student.j2)
- [Learner](roles/common/templates/Dockerfile.learner.j2)
- [Grader](roles/common/templates/Dockerfile.grader.j2)

The nbgrader extensions are enabled within the images like so:

|   | Students  | Instructors  | Formgraders  |
|---|---|---|---|
| Create Assignment  | no  | no  | yes  |
| Assignment List  | yes  | yes | no  |
| Formgrader  | no  | no  | yes  |
| Course List | no  | yes  | no  |

Refer to [this section](https://nbgrader.readthedocs.io/en/stable/user_guide/installation.html#installing-and-activating-extensions) of the `nbgrader` docs for more information on how you can enable and disable specific extensions.

### Grading with Multiple Instructors

As of `nbgrader 0.6.0`, nbgrader supports the [JupyterHubAuthPlugin](https://nbgrader.readthedocs.io/en/stable/configuration/jupyterhub_config.html#jupyterhub-authentication) to determine the user's membership within a course. The section that describes how to run [nbgrader with JupyterHub] is well written. However for the sake of clarity, some of the key points and examples are written below.

The following rules are defined to determine access to nbgrader features:

- Users with the student role are members of the `nbgrader-{course_id}` group(s). Students are shown assignments only for course(s) with `{course_id}`.
- Users with the instructor role are members of the `formgrade-{course_id}` group(s). Instructors are shown links to course(s) to access `{course_id}`. To access the formgrader, instructors access to the `{course_id}` service (essentially a shared notebook) and authenticate to the `{course_id}` service using JupyterHub as an OAuth2 server.

> **NOTE** It's important to emphasize that **instructors do not grade assignments with their own notebook server** but with a **shared notebook** which runs as a JupyterHub service and which is owned by the shared `grader-{course_id}` account.

The configuration for this setup is located in four locations. The first deals with the grader notebook as an [externally managed JupyterHub service](https://jupyterhub.readthedocs.io/en/stable/getting-started/services-basics.html), and the other three deal with the location and settings for `nbgrader_config.py`.

The examples below use the `course101` as the course name (known as `context_label` in LTI terms):

1. Within `jupyterhub_config.py` which defines a service:

- Name
- Access by group
- Ownership
- API token
- URL
- Command

For example:

```python
c.JupyterHub.services = [
    {
        'name': 'course101',
        'url': 'http://127.0.0.1:9999',
        'command': [
            'jupyterhub-singleuser',
            '--group=formgrade-course101',
            '--debug',
        ],
        'user': 'grader-course101',
        'cwd': '/home/grader-course101',
        'api_token': 'api_token_course101'
    }]
```

2. The global `nbgrader_config.py` used by all roles, located in `/etc/jupyter/nbgrader_config.py` which defines:

- Authenticator plugin class
- Exchange directory location

For example:

```python
c.Exchange.path_includes_course = True
c.Exchange.root = '/srv/nbgrader/exchange'
c.Authenticator.plugin_class = JupyterHubAuthPlugin
```

3. The `nbgrader_config.py` located within the shared grader account home directory: (`/home/grader-course101/.jupyter/nbgrader_config.py`) which defines:

- Course root path
- Course name

For example:

```python
c.CourseDirectory.root = '/home/grader-course101/course101'
c.CourseDirectory.course_id = 'course101'
```

4. The `nbgrader_config.py` located within the course directory: (`/home/grader-course101/course101/nbgrader_config.py`) which defines:

- The course_id
- Nbgrader application options

For example:

```python
c.CourseDirectory.course_id = 'course101'
c.ClearSolutions.text_stub = 'ADD YOUR ANSWER HERE'
```

### Some Notes on Authentication, User Directories, and Local System Users

The examples provided in this repo assume that users are **not** local system users. A custom
`Spawner.pre_spawn_hook` is used to create user directories before spawing their notebook.

## Environment Variables

The services included with this setup rely on environment variables to work properly. You can override them by either setting the ansible veriable when running the playbook or my manually modifying the environment variables on the `env.*` host files after the playbook has run.

### Environment Variables pertaining to JupyterHub, located in `env.jhub`

| Variable  |  Type | Description | Default Value |
|---|---|---|---|
| CONFIGURABLE_HTTP_PROXY | `string` | Random string used to authenticate the proxy with JupyterHub and vs. | `<random_string_value>` |
| COURSE_ID | `string` | Demo course id, equivalent to course name or course label. | `intro101` |
| DEMO_INSTRUCTOR_NAME | `string` | Demo instructor user name. | `instructor1` |
| DEMO_INSTRUCTOR_GROUP | `string` | Demo instructor group name. | `formgrade-{course_id}` |
| DEMO_STUDENT_GROUP | `string` | Demo student group name. | `nbgrader-{course_id}` |
| DEMO_GRADER_NAME | `string` | Demo grader service name. | `service-{course_id}` |
| DOCKER_LEARNER_IMAGE | `string` | Docker image used by users with the Learner role. | `illumidesk/notebook:learner` |
| DOCKER_GRADER_IMAGE | `string` | Docker image used by users with the Grader role. | `illumidesk/notebook:grader` |
| DOCKER_INSTRUCTOR_IMAGE | `string` | Docker image used by users with the Instructor role. | `illumidesk/notebook:instructor` |
| DOCKER_STANDARD_IMAGE | `string` | Docker image used by users without an assigned role. | `illumidesk/notebook:standard` |
| DOCKER_NETWORK_NAME | `string` | Docker network name for docker-compose and dockerspawner | `illumidesk-network` |
| DOCKER_NOTEBOOK_DIR | `string` | Working directory for Jupyter Notebooks | `/home/jovyan` |
| EXCHANGE_DIR | `string` | Exchange directory path  | `/srv/nbgrader/exchange` |
| JUPYTERHUB_CRYPT_KEY | `string` | Cyptographic key used to encrypt cookies. | `<random_value>` |
| JUPYTERHUB_API_TOKEN | `string` | API token used to authenticate grader service with JupyterHub. | `<random_value>` |
| JUPYTERHUB_API_TOKEN_USER | `string` | Grader service user which owns JUPYTERHUB_API_TOKEN. | `grader-{course_id}` |
| JUPYTERHUB_API_URL | `string` | Internal API URL corresponding to JupyterHub. | `http://jupyterhub:8081` |
| LTI_CONSUMER_KEY | `string` | LTI 1.1 consumer key | `my_consumer_key` |
| LTI_SHARED_SECRET | `string` | LTI 1.1 shared secret | `my_shared_secret` |
| MNT_HOME_DIR_UID | `string` | Host user directory UID | `1000` |
| MNT_HOME_DIR_GID | `string` | Host user directory GID | `100` |
| MNT_ROOT | `string` | Host directory root | `/mnt` |
| ORGANIZATION_NAME | `string` | Organization name. | `my-edu` |
| PGDATA | `string` | Postgres data file path | `/var/lib/postgresql/data` |
| POSTGRES_DB | `string` | Postgres database name | `jupyterhub` |
| POSTGRES_USER | `string` | Postgres database username | `jupyterhub` |
| POSTGRES_PASSWORD | `string` | Postgres database password | `jupyterhub` |
| POSTGRES_HOST | `string` | Postgres host | `jupyterhub-db` |

### Environment Variables pertaining to grader service, located in `env.service`

| Variable  |  Type | Description | Default Value |
|---|---|---|---|
| JUPYTERHUB_API_TOKEN | `string` | JupyterHub API token | `<randon_value>` |
| JUPYTERHUB_API_URL | `string` | External facing API URL | `http://reverse-proxy:8000/hub/api` |
| JUPYTERHUB_CLIENT_ID | `string` | JupyterHub client id used with OAuth2 | `service-{course_id}` |
| JUPYTERHUB_SERVICE_PREFIX | `string` | JupyterHub client id used with OAuth2 | /`services/{course_id}` |
| NB_USER | `string` | Notebook grader user | `grader-{course_id}` |
| NB_UID | `string` | Notebook grader user id | `10001` |

---

## Resources

### Documentation

- [JupyterHub documentation](https://jupyterhub.readthedocs.io/en/stable/)
- [JupyterHub API](https://jupyterhub.readthedocs.io/en/stable/api/)
- [Nbgrader documentation](https://nbgrader.readthedocs.io/en/stable/)

### Sources of Inspiration

- [jupyterhub-deploy-docker](https://github.com/jupyterhub/jupyterhub-deploy-docker)
- [jupyterhub-docker](https://github.com/defeo/jupyterhub-docker)

### General Guidelines

This project enforces the [Contributor Covenant](./CODE_OF_CONDUCT.md). Be kind and build a nice open source community with us.

### License

MIT
