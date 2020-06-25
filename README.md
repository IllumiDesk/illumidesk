[![Build Status](https://travis-ci.com/IllumiDesk/illumidesk.svg?branch=main)](https://travis-ci.com/IllumiDesk/illumidesk)
[![codecov](https://codecov.io/gh/IllumiDesk/illumidesk/branch/main/graph/badge.svg)](https://codecov.io/gh/IllumiDesk/illumidesk)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Code style black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# IllumiDesk

## Overview

[Jupyter Notebooks](https://jupyter.org) are a great **education tool** for a variety of subjects since it offers instructors and learners a unified document standard to combine markdown, code, and rich visualizations. With the proper setup, Jupyter Notebooks allow organizations to enhance their learning experiences.

When combined with the [nbgrader](https://github.com/jupyter/nbgrader) package instructors are able to automate much of tasks associated with grading and providing feedback for their users.

## Why?

Running a multi-user setup using [JupyterHub](https://github.com/jupyterhub/jupyterhub) and `nbgrader` with `docker containers` requires some additional setup. Some of the questions this distribution attempts to answer are:

- How do we manage authentication when the user isn't a system user within the JupyterHub or Jupyter Notebook container?
- How do we manage permissions for student and instructor folders?
- How do we securely syncronize information with the Learning Management System (LMS) using the [LTI 1.1 and LTI 1.3](https://www.imsglobal.org/activity/learning-tools-interoperability) standards?
- How do we improve the developer experience to provide more consistency with versions used in production, such as with Kubernetes?
- How should deployment tools reflect these container-based requirements and also (to the extent possible) offer users an option that is cloud-vendor agnostic?

Our goal is to remove these obstacles so that you can get on with the teaching!

## Quick Start

Follow these instructions to install the system with a set of sensible defaults.

Refer to the [customization](#customization) section for more advanced setup options, such as enabling LTI to handle requests from your LMS.

### Prerequisites

On remote host:

- Tested with Ubuntu 18.04

### Prepare your setup

1. Clone and change directories into this repo's root:

```
git clone https://github.com/IllumiDesk/illumidesk
cd illumidesk
```

2. Create a new hosts file from the provided YML template.

```
cp ansible/hosts.example ansible/hosts
```

3. Update the `ansible/hosts` file:
  
    - ansible_host: target server IPv4 address
    - ansible_port: target server port (default 22)
    - ansible_user: target server username for SSH access
    - ansible_ssh_private_key_file: full path to SSH private key file used for SSH
    - ansible_password: optional value used when the target server requires a username/password

By default this setup uses the `FristUseAuthenticator`. Refer to the [customization](#customization) section if you would like to use LTI 1.1 with your LMS.

4. Run the deployment script (the script will prompt you for certain values):

    ```bash
    make deploy
    ```

Use the `ARGS="-v"` option to deploy the stack with verbosity enabled. For example:

    ```bash
    make deploy ARGS="-v"
    ```

Set `ARGS` to `-vv` to enable more verbosity or `-vvv` for super duper verbosity.

5. Once the ansible playbook has finished running the stack should be available at:

    `http://<target_ipv4>:8000/`

6. Login with either the instructor or student accounts:

- **Instructor Role**: instructor1
- **Student Role**: student1

> **Tip**: To confirm the values you will need for the `make deploy` command to successfully connect to your instance, log into your remote instance with SSH. For example, a successfull connection with the `ssh -i my-ssh-key.pem ubuntu@1.2.3.4` command means that the values map to:

> - ansible_host: 1.2.3.4
> - ansible_port: 22
> - ansible_user: ubuntu
> - ansible_ssh_private_key_file: my-ssh-key.pem
> - ansible_password: (none)

### Initial Course Setup

By default, this setup uses the `FirstUseAuthenticator` and as such accepts any password you designate when first logging into the system.

1. Log in with the instructor account which by default is `instructor1`

2. Access the shared grader notebook accessible by clicking on `Control Panel --> Services --> Course ID` (`intro101` by default)

3. Open a Jupyter terminal by clicking on `New --> Terminal`.

4. Type `nbgrader quickstart intro101 --force`

5. Click on the `Grader Console` tab and follow the steps available within the nbgrader docs to generate and release assignments for the students.

## Components

* **JupyterHub**: Runs [JupyterHub](https://jupyterhub.readthedocs.org/en/latest/getting-started.html#overview) within a Docker container running as root.

* **Authenticator**: Authentication service. This setup relies on the [FirstUseAuthenticator](https://github.com/jupyterhub/firstuseauthenticator).

* **Spawner**: Spawning service to manage user notebooks. This setup uses [DockerSpawner](https://github.com/jupyterhub/dockerspawner).

* **Data Directories**: This repo uses `docker-compose` to start all services and data volumes for JupyterHub, notebook directories, databases, and the `nbgrader exchange` directory using mounts from the host's file system.

* **Databases**: This setup relies on a standard `postgres` database running in its own container for the JupyterHub application and another separate and optional Postgres database for lab environments (useful to connect from user notebooks).

* **Network**: An external bridge network named `jupyter-network` is used by default. The grader service and the user notebooks are attached to this network.

## Customization

You may customize your setup by customizing additional variables in the `hosts` file. For example, you can run the `make deploy` command to set your own organization name and top level domain when using this setup behind a reverse-proxy with TLS termination.

> **NOTE**: You may add any of the variables listed in `ansible/group_vars/all.yml` within your `hosts` file before running the `make deploy` command.

### LTI 1.3 Authenticator

> **New in Version 0.6.0**: this setup supports user authentication with the [LTI 1.3 Core Specification](http://www.imsglobal.org/spec/lti/v1p3/) as of version 0.6.0. LTI 1.3 is built on top of OAuth2 and OIDC and therefore provides additional security features when compared to [LTI 1.1](https://www.imsglobal.org/specs/ltiv1p1).

To enable LTI 1.3, update your ansible `hosts` configuration so that `lti13_enabled` is set to `true`. Then, add the platform (usually an LMS) endpoints required to establish a trust relationship between the tool and the platform. These additional endpoints are provided by the `lti13_private_key`, `lti13_endpoint`, `lti13_token_url`, and `lti13_authorize_url`. You also need to specify the `lti13_client_id` used by the platform to associate the tool with an OIDC compatible client id. The [`hosts.example`](./ansible/hosts.example) has some example endpoints. Keep in mind however, that unlike LTI 1.1 (instructions below), LTI 1.3's trust relationsip between the platform and the tool is explicit.

Please refer to [the user guide documentation](https://app.gitbook.com/@illumidesk/s/guides/installation-and-configuration/learning-tools-interoperability-lti-1.3) if you need instructions on how to configure the tool using the LTI 1.3 option with specific LMS vendors.

### LTI 1.1 Authenticator

> **New in Version 0.2.0**: with LTI 1.1 enabled, courses and user membership are automatically set for you based on the information located within the LTI 1.1 launch request. This feature allows you to dynamically support multiple classes with multiple teacher/learner memberships from the same deployment without haveing to update the configuration files.

To launch the stack with LTI 1.1 enabled simply change the `lti11_enabled` variable in your hosts file to `true`.
By default both the `consumer key` and `shared secret` are created for you. If you would like to add your own
values then assign them to the `lti11_consumer_key` and `lti11_shared_secret` variables in the `hosts` file.

Then, rerun the `make deploy` copmmand to update your stack's settings.

### Postgres for Lab Environments

> **New in Version 0.5.0**: users that wish to provide their Learners with a shared Postgres container my do so by setting the `postgres_labs_enabled` to true.

With the Postgres container enabled, users (both students and instructors) can connect to a shared Postgres database from within their Jupyter Notebooks by opening a connection with the standard `psycop2g` depency using the `postgres-labs` host name. IllumiDesk's [user guides provide additional examples](https://docs.illumidesk.com) on the commands and common use-cases available for this option.


### Defining Launch Requests to Clone / Merge Git-based Repos

Instructors and content creators in many cases have their content version controlled with git-based source control solutions, such as GitHub, GitLab, or BitBucket. This setup includes the [`nbgitpuller`](https://pypi.org/project/nbgitpuller/) package and handles LTI launch requests to clone and merge source files from an upstream git-based repository.

This functionality is decoupled from the authenticator, therefore, the options are added as query parameters when sending the POST request to the hub. Below are the definition setting and an example of a full launch request URL using LTI 1.1:

- repo: the repositories full URL link
- branch: the git branch you would like users to clone from
- subPath: folder and path name for the file you would like your users to open when first launching the URL
- app: one of `notebook` for Classic Notebook, `lab` for JupyerLab, `theia` for THEIA IDE.

For example, if your values are:

- IllumiDesk launch request URL: https://acme.illumidesk.com/lti/launch
- repo: https://github.com/acme/intro-to-python
- branch: master
- subPath: 00_intro_00_content.ipynb
- app: notebook

Then the full launch request URL would look like so:

```
https://acme.illumidesk.com/lti/launch?next=/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Facme%2Fintro-to-python&branch=master&subPath=00_intro_00_content.ipynb&app=notebook
```

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

5. Cloud specific setup options by specifying settings in the `hosts` file. For now, these options are specific to `AWS EFS` mounts. This allows administrators to leverage AWS's EFS service for additional data redundancy, security, and sharing options. Shared file systems are particularly helpful when using a setup with multiple hosts such as with Docker Swarm or Kubernetes since the user's container may launch on any available virtual machine (host). To enable and use EFS, update the following `hosts` file variables:

- **aws_efs_enabled (Required)**: set to true to enable mounts with AWS EFS, defaults to `false`.
- **aws_region (Required)**: the AWS region where the EFS service is running, defaults to `us-west-2`.
- **efs_id (Required)**: and existing AWS EFS identifier, for example `fs-0726eyyd`. Defaults to an empty string.
- **mnt_root (Recommended)**: if you test without NFS-based mounts and then mount an existing folder to an NFS-based shared directory, then you run the risk of losing your files. Change this value to use a folder other than the default `/mnt` directory to either another directory or a sub-directory within the `/mnt` directory, such as `/mnt/efs/fs1`.

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

As mentioned in the [authenticator](#authenticator) section, make sure you refer to the spawner's documentation to consider all settings before launching JupyterHub. In most cases the spawners provide drop-in replacement of the provided IllumiDeskDockerSpawner class, however, setting other spawners may break compatibility with the grading services.

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
| COURSE_ID | `string` | Demo course id, equivalent to course name or course label. | `intro101` |
| DEMO_INSTRUCTOR_NAME | `string` | Demo instructor user name. | `instructor1` |
| DEMO_INSTRUCTOR_GROUP | `string` | Demo instructor group name. | `formgrade-{course_id}` |
| DEMO_STUDENT_GROUP | `string` | Demo student group name. | `nbgrader-{course_id}` |
| DEMO_GRADER_NAME | `string` | Demo grader service name. | `service-{course_id}` |
| DOCKER_LEARNER_IMAGE | `string` | Docker image used by users with the Learner role. | `illumidesk/notebook:learner` |
| DOCKER_GRADER_IMAGE | `string` | Docker image used by users with the Grader role. | `illumidesk/notebook:grader` |
| DOCKER_INSTRUCTOR_IMAGE | `string` | Docker image used by users with the Instructor role. | `illumidesk/notebook:instructor` |
| DOCKER_STANDARD_IMAGE | `string` | Docker image used by users without an assigned role. | `illumidesk/notebook:standard` |
| DOCKER_THEIA_IMAGE | `string` | Docker image used for the THEIA IDE | `illumidesk/theiaide:latest` |
| DOCKER_RSTUDIO_IMAGE | `string` | Docker image used for RStudio | `illumidesk/rstudio:latest` |
| DOCKER_VSCODE_IMAGE | `string` | Docker image used for VS Code | `illumidesk/vscode:latest` |
| DOCKER_NETWORK_NAME | `string` | Docker network name for docker-compose and dockerspawner | `jupyter-network` |
| DOCKER_NOTEBOOK_DIR | `string` | Working directory for Jupyter Notebooks | `/home/jovyan` |
| EXCHANGE_DIR | `string` | Exchange directory path  | `/srv/nbgrader/exchange` |
| JUPYTERHUB_CRYPT_KEY | `string` | Cyptographic key used to encrypt cookies. | `<random_value>` |
| JUPYTERHUB_API_TOKEN | `string` | API token used to authenticate grader service with JupyterHub. | `<random_value>` |
| JUPYTERHUB_API_TOKEN_USER | `string` | Grader service user which owns JUPYTERHUB_API_TOKEN. | `grader-{course_id}` |
| JUPYTERHUB_API_URL | `string` | Internal API URL corresponding to JupyterHub. | `http://jupyterhub:8081` |
| LTI_CONSUMER_KEY | `string` | LTI 1.1 consumer key | `ild_test_consumer_key` |
| LTI_SHARED_SECRET | `string` | LTI 1.1 shared secret | `ild_test_shared_secret` |
| LTI13_AUTHORIZE_URL | `string` | LTI 1.3 authorization URL, such as `https://my.platform.domain/api/lti/authorize_redirect` | `''` |
| LTI13_CLIENT_ID | `string` | LTI 1.3 client id used to identify the tool's installation within the platform, such as `125900000000000071` | `''` |
| LTI13_ENDPOINT | `string` | LTI 1.3 platform endpoint, such as `https://my.platform.domain/api/lti/security/jwks` | `''` |
| LTI13_PRIVATE_KEY | `string` | Private key used with LTI 1.3 to create public JSON Web Keys (JWK) | `/secrets/keys/rsa_private.pem` |
| LTI13_TOKEN_URL | `string` | LTI 1.3 token URL surfaced by the platform, such as `https://my.platform.domain/login/oauth2/token` | `''` |
| MNT_HOME_DIR_UID | `string` | Host user directory UID | `1000` |
| MNT_HOME_DIR_GID | `string` | Host user directory GID | `100` |
| MNT_ROOT | `string` | Host directory root | `/mnt` |
| ORGANIZATION_NAME | `string` | Organization name. | `my-edu` |
| PGDATA | `string` | Postgres data file path | `/var/lib/postgresql/data` |
| POSTGRES_DB | `string` | Postgres database name | `jupyterhub` |
| POSTGRES_USER | `string` | Postgres database username | `jupyterhub` |
| POSTGRES_PASSWORD | `string` | Postgres database password | `jupyterhub` |
| POSTGRES_HOST | `string` | Postgres host | `jupyterhub-db` |
| USER_WORKSPACE_TYPE | `string` | User's workspace type to run | `notebook` |

### Environment Variables pertaining to grader service, located in `env.service`

> This file is only used when you're using the initial setup with FirstUseAuthenticator

| Variable  |  Type | Description | Default Value |
|---|---|---|---|
| JUPYTERHUB_API_TOKEN | `string` | JupyterHub API token | `<randon_value>` |
| JUPYTERHUB_API_URL | `string` | External facing API URL | `http://reverse-proxy:8000/hub/api` |
| JUPYTERHUB_CLIENT_ID | `string` | JupyterHub client id used with OAuth2 | `service-{course_id}` |
| JUPYTERHUB_SERVICE_PREFIX | `string` | JupyterHub client id used with OAuth2 | /`services/{course_id}` |
| NB_USER | `string` | Notebook grader user | `grader-{course_id}` |
| NB_UID | `string` | Notebook grader user id | `10001` |

### Environment Variables pertaining to setup-course service, located in `env.setup-course`

| Variable  |  Type | Description | Default Value |
|---|---|---|---|
| DOCKER_NETWORK_NAME | `string` | JupyterHub API token | `jupyter-network` |
| GRADER_SERVICE_IMAGE | `string` | External facing API URL | `http://reverse-proxy:8000/hub/api` |
| ILLUMIDESK_DIR | `string` | IllumiDesk working directory within remote user's home directory | `$HOME/illumidesk_deployment` |
| JUPYTERHUB_API_TOKEN | `string` | API token to connect with the JupyterHub | `<random value>` |
| JUPYTERHUB_API_URL | `string` | JupyterHub client id used with OAuth2 | `http://reverse-proxy:8000/hub/api` |
| JUPYTERHUB_CONFIG_PATH | `string` | Notebook grader user | `/srv/jupyterhub` |
| JUPYTERHUB_SERVICE_NAME | `string` | Notebook grader user id | `jupyterhub` |
| MNT_ROOT | `string` | Notebook grader user id | `/mnt` |
| NB_UID | `string` | Notebook grader user id | `10001` |
| NB_GID | `string` | Notebook grader user id | `100` |

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

Please refer to the included [license](./LICENSE) in this repository's root directory.
