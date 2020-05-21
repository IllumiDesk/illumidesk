# Contributor Guide

## Contributor license agreement

By submitting code as an individual you agree to the [individual contributor license agreement](./docs/legal/individual_contributor_license_agreement.md). By submitting code as an entity you agree to the [corporate contributor license agreement](./docs/legal/corporate_contributor_license_agreement.md). All Documentation content that resides under the doc/ directory of this repository is licensed under [Creative Commons: CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode).

## General Guidelines

This project enforces the [Contributor Covenant](./CODE_OF_CONDUCT.md). Be kind and build a nice open source community with us.

## How do I make a contribution?

Never made an open source contribution before? Wondering how contributions work
in the nteract world? Here's a quick rundown!

1.  Find an issue that you are interested in addressing or a feature that you would like to address.
2.  Fork the repository associated with the issue to your local GitHub organization.
4.  Clone the repository to your local machine using:

```
$ git clone https://github.com/github-username/repository-name.git
```

5.  Install the dependencies required for the project by running:

```
$ make dev
```

6.  Create a new branch for your feature or fix using:

```
$ git checkout -b branch-name-here
```

7.  Make the appropriate changes for the issue you are trying to address or the feature that you want to add. Validate your changes by following the steps in the "How do I validate my changes" segment below.
8.  Confirm that unit tests still pass successfully with:

```
$ python3 -m pytest
```
If tests fail, don't hesitate to ask for help.

9.  Add and commit the changed files using `git add` and `git commit -m "my commit message here"`. You may notice that some commands run right after running `git commit ...`.
10. Push the changes to your fork using:

```
$ git push origin branch-name-here
```
11. Submit a pull request to the upstream repository.
12. Title the pull request per the requirements outlined in the section below.
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

The CI/CD pipeline will check coding style but will not error out. There may be situations where minor coding style errors are less important that in important merges to the master trunk. However, these are considered on a case-by-case basis.

## Commit Messages, Changelog, and Releases

### For Contributors

This project uses Semantic Versioning with Conventional Commits to track major, minor, and patch releases. The `npm run release` command automates [CHANGLOG.md](./CHANGELOG.md) updates and release version metadata.

Once a new version is released, assets should be published with the new tag, such as docker images, pip/npm packages, and GitHub repo release tags.

For the most part, contributors do not need to worry about commit message formats, since all commits from a Pull Request are squashed and merged before merging to master. Commit messages are updated to the standard format during this step.

### For Maintainers

When squashing and merging to the `master` branch, use the following format to provide consistent updates to the `CHANGELOG.md` file:

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
