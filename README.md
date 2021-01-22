[![Build Status](https://travis-ci.com/IllumiDesk/illumidesk.svg?branch=main)](https://travis-ci.com/IllumiDesk/illumidesk)
[![codecov](https://codecov.io/gh/IllumiDesk/illumidesk/branch/main/graph/badge.svg)](https://codecov.io/gh/IllumiDesk/illumidesk)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Code style black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# IllumiDesk

This monorepo is used to maintain IllumiDesk's authenticators, spawners, and microservices. This setup assumes that all services are running with Kubernetes.
Please refer to our [help guides](https://help.illumidesk.com) for more information.

## Overview

[Jupyter Notebooks](https://jupyter.org) are a great **education tool** for a variety of subjects since it offers instructors and learners a unified document standard to combine markdown, code, and rich visualizations. With the proper setup, Jupyter Notebooks allow organizations to enhance their learning experiences.

When combined with the [nbgrader](https://github.com/jupyter/nbgrader) package instructors are able to automate much of tasks associated with grading and providing feedback for their users.

## Why?

Running a multi-user setup using [JupyterHub](https://github.com/jupyterhub/jupyterhub) and `nbgrader` with `containers` requires some additional setup. Some of the questions this distribution attempts to answer are:

- How do we manage authentication when the user isn't a system user within the JupyterHub or Jupyter Notebook container?
- How do we manage permissions for student and instructor folders?
- How do we securely syncronize information with the Learning Management System (LMS) using the [LTI 1.1 and LTI 1.3](https://www.imsglobal.org/activity/learning-tools-interoperability) standards?
- How do we improve the developer experience to provide more consistency with versions used in production, such as with Kubernetes?
- How should deployment tools reflect these container-based requirements and also (to the extent possible) offer users an option that is cloud-vendor agnostic?

Our goal is to remove these obstacles so that you can get on with the teaching!
## Prerequisites

Kubernetes v1.17+.
## Quick Start

This setup only supports Kubernetes-based installations at this time. Refer to the [helm-chart](https://github.com/illumidesk/helm-chart) repo for installation instructions.

## Development Installation

Refer to the [contributing](./CONTRIBUTING.md) guide located in the root of this repo.
### General Guidelines

This project enforces the [Contributor Covenant](./CODE_OF_CONDUCT.md). Be kind and build a nice open source community with us.

### License

Please refer to the included [license](./LICENSE) in this repository's root directory.
