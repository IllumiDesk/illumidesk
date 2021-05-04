# Contributor Guide

## Contributor license agreement

By submitting code as an individual you agree to the [individual contributor license agreement](./docs/legal/individual_contributor_license_agreement.md). By submitting code as an entity you agree to the [corporate contributor license agreement](./docs/legal/corporate_contributor_license_agreement.md). All Documentation content that resides under the doc/ directory of this repository is licensed under [Creative Commons: CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode).

## General Guidelines

This project enforces the [Contributor Covenant](./CODE_OF_CONDUCT.md). Be kind and build a nice open source community with us.

## How do I make a contribution?

Never made an open source contribution before? Wondering how contributions work
in the IllumiDesk world? Here's a quick rundown!

1.  Fork this repository with GitHub's `Fork` option.
2.  Clone the repository to your local machine using:

```
$ git clone `https://github.com/<github-account>/illumidesk.git`
```

5.  Install the dependencies required for the project by running:

```
$ make dev
$ source venv/bin/activate
```

or

```bash
$ virtualenv -p python3 venv
$ python3 -m pip install -r dev-requirements.txt
$ source venv/bin/activate
```

6.  Create a new branch for your feature or fix using:

```
$ git checkout -b branch-name-here
```

7.  Make the appropriate changes for the issue you are trying to address or the feature that you want to add. Validate your changes by following the steps in the [Validate Changes](#validate-changes) segment below.

8.  Add and commit the changed files using `git add` and `git commit -m "my commit message here"`. You may notice that some commands run right after running `git commit ...`. These commands are run with the `pre-commit` hooks defined in the `.pre-commit-config.yaml` configuration file.

9. Push the changes to your fork using:

```
$ git push origin branch-name-here
```

11. Submit a pull request to the upstream repository.
12. Title the pull request per the requirements outlined in the [Commits and Merges](#commits-and-merges) section.
13. Set the description of the pull request with a brief description of what you did and any questions you might have about what you did.
14. Wait for the pull request to be reviewed by a maintainer.
15. Make changes to the pull request if the reviewing maintainer recommends them.
16. Celebrate your success after your pull request is merged! :tada:

## Coding Style

This project uses Python and Javascript (for the most part). We use the following tools to enforce coding style:

- Format code with [black](https://github.com/psf/black). For those of you familiar with go, this is equivalent to `go fmt`.
- Check code style with `flake8`. The rules to check code style using flake8 are aligned with black's rules to avoid conflicts.
- We document code wherever possible using docstrings. Generally speaking we align ourselves to [Google's python style guide](http://google.github.io/styleguide/pyguide.html).
- Verify coding style for domain specific languages, such as ansible, with independent tools, even though they may be based on python and/or javascript.

Linters and formatters are set up with pre-commit-hooks. If you aren't used to pre-commit hooks you may gasp for oxygen once you attempt to commit your changes for the first time. Even when you do get used to it the idea of having to run the same add/commit multiple times may be nerve racking. (Ok so there is a little drama in there, its not that bad). Having the pre-commit-hooks in place helps speed up the PR review process so we can focus on the important stuff.

The CI/CD pipeline will check coding style but will not error out. There may be situations where minor coding style errors are less important that in important merges to the `main` branch. However, these are considered on a case-by-case basis.

## Commit Messages, Changelog, and Releases

This project includes `pre-commit` hooks configured to run `black`, `flake8`, and `pip-compile` before running and completing the `git commit ...` command. If these tools do not run when running the `git add ...` and `git commit ...` commands, make sure you install the pre-commit hooks with `pre-commit install`.

### For Contributors

This project uses Semantic Versioning with Conventional Commits to track major, minor, and patch releases. The `npm run release` command automates [CHANGLOG.md](./CHANGELOG.md) updates and release version metadata.

Once a new version is released, assets should be published with the new tag, such as docker images, pip/npm packages, and GitHub repo release tags.

For the most part, contributors do not need to worry about commit message formats, since all commits from a Pull Request are squashed and merged before merging to `main`. Commit messages are updated to the standard format during this step.

### For Maintainers

#### Commits and merges

When squashing and merging to the `main` branch, use the following format to provide consistent updates to the `CHANGELOG.md` file:

    <Commit Type>(scope): <Merge Description>

- `Merge Description` should initiate with a capital letter, as it provides the changelog with a standard sentence structure.

- `Scope` is used to define what is being updated. Our current scopes include:

1. core
3. grader
4. workspace

- `Commit Types` are listed below:

| Commit Type | Commit Format |
| --- | --- |
| Chores | `chore` |
| Documentation | `docs` |
| Features | `feat` |
| Fixes | `fix` |
| Refactoring | `refactor` |

Use the `BREAKING CHANGE` in the commit's footer if a release has a breaking change.

Examples:

- Commit a new feature:

    ```
    feat(workspace): Publish static notebooks with live widgets
    ```

- Commit a bug fix:

    ```
    fix(core): Allow students to open submitted assignments from grades section
    ```

- Commit a version with a breaking change:

    ```
    feat(core): Deprecate observer role from group memberships

    BREAKING CHANGE: `extends` key in config file is now used for extending other config files
    ```

## Validate Changes

This setup contains one Kubernetes compatible microservice and one Python package meant to run with a JupyterHub instance:

- `src/illumidesk`: Python package structured as JupyterHub Authenticators for LTI Authenticators (1.1 and 1.3).
- `src/graderservice`: Kubernetes compatible RESTful API running as a JupyterHub externally managed service which is used to set up shared grader notebooks.

To validate your changes, it may be necessary to run both unit and integration tests for both the `graderservice` RESTful API and the `illumidesk` Python package.

### Unit Tests

Confirm that unit tests still pass successfully:

```
$ cd src/illumidesk
$ python3 -m pytest
```
or

```
$ cd src/graderservice
$ python3 -m pytest
```

### Integration Tests

A `Dockerfile` is provided in the `src/graderservice` and the `src/illumidesk` folders to facilitate **basic** integration testing. Use the command below to build the docker images:

1. Change directory into the `src/illumidesk` or `src/graderservice` folder.
2. Run the docker build command to create the docker image (replace tag with your desired tag, such as `dev`):

```bash
$ cd src/illumidesk
$ docker build -t illumidesk/jupyterhub:<tag>
$ cd src/graderservice
$ docker build -t illumidesk/graderservice:<tag>
```

3. Run the `illumidesk/jupyterhub:<tag>` and the `illumidesk/jupyterhub:<tag>` as docker containers:

```bash
docker run -d -p 8000:8000 -v $HOME:/home/jovyan/ illumidesk/graderservice:<tag>
```

> **NOTE**: this step requires you to have the `kubectl` client installed and connected with your `Kubernetes` configuration file, `.kubeconfig`. Please refer to the official [Kuberentes documentation for additional setup instructions](https://kubernetes.io/docs/tasks/tools/).

4. Test a `graderservice` endpoints using `curl` or any other client capable of sending http requests. Here are some examples with the `curl` command:

Fetch a list of JupyterHub services that represent shared grader notebooks:

```bash
curl -v http://localhost:8000/services
```

Create a new shared grader notebook with the `acme` organization and `intro101` course id:

```bash
curl -v -X POST http://localhost:8000/services/acme/intro101
```

If tests fail, don't hesitate to ask for help.

#### Pre-commit hooks

This repo includes the `pre-commit` setup with:

- black: code formatting
- flake8: python linter
- isort: imports organizer

To enable the pre-commit hook in your local environment,

**Updating the Changelog Format**

Refer to the official [`standard-version`](https://github.com/conventional-changelog/standard-version) docs to update the `CHANGELOG.md` template with additional options.

**Releases**

IllumiDesk uses [`semantic versioning`](https://semver.org) with this monorepo. To create a new release, use the commands available with the `npm run release` command. (Make sure you run `npm install` to install required dependencies).

Merges that conclude a [milestone](https://github.com/IllumiDesk/illumidesk/milestones) `SHOULD` update and tag the release. Versions are managed as major, minor, or patch releases. Generally speaking:

```
- MAJOR version when you make incompatible or breaking API changes,
- MINOR version when you add functionality in a backwards compatible manner, and
- PATCH version when you make backwards compatible bug and security fixes.

Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.
```

Examples:

Automatically create a new minor release:

    npm run release -- --release-as minor

Cut a new release with a specific tag:

    npm run release -- --release-as 1.1.0

Refer to the [`standard-version`](https://github.com/conventional-changelog/standard-version) for additional release command options.
