# Python Semantic Release Guidelines

This project uses [python-semantic-release](https://python-semantic-release.readthedocs.io/) for automated version management and package publishing. Python-semantic-release automatically determines the next version number, generates release notes, and publishes the package based on your commit messages.

## Commit Message Format

Python-semantic-release uses the [Angular Commit Message Conventions](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-format) to determine the version bump and generate release notes.

### Commit Message Structure

```
<type>(<scope>): <short summary>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

The `<type>` and `<summary>` fields are mandatory, the `(<scope>)` field is optional.

### Type

Must be one of the following:

* **feat**: A new feature (triggers a minor version bump)
* **fix**: A bug fix (triggers a patch version bump)
* **docs**: Documentation only changes
* **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
* **refactor**: A code change that neither fixes a bug nor adds a feature
* **perf**: A code change that improves performance
* **test**: Adding missing tests or correcting existing tests
* **build**: Changes that affect the build system or external dependencies
* **ci**: Changes to our CI configuration files and scripts
* **chore**: Other changes that don't modify src or test files
* **revert**: Reverts a previous commit

### Scope

The scope should be the name of the module affected (as perceived by the person reading the changelog generated from commit messages).

### Subject

The subject contains a succinct description of the change:

* Use the imperative, present tense: "change" not "changed" nor "changes"
* Don't capitalize the first letter
* No dot (.) at the end

### Body

Just as in the subject, use the imperative, present tense: "change" not "changed" nor "changes". The body should include the motivation for the change and contrast this with previous behavior.

### Breaking Changes

Breaking changes should start with the word `BREAKING CHANGE:` with a space or two newlines. The rest of the commit message is then used for this.

## Examples

```
feat(api): add ability to retrieve user profile

fix(auth): resolve issue with token refresh

docs: update README with new API endpoints

style: format code according to linting rules

refactor(database): optimize query performance

perf: improve image loading time

test: add unit tests for auth service

BREAKING CHANGE: drop support for Python 3.7
```

## Release Types

Python-semantic-release will determine the release type based on the commits:

* **patch**: Bug fixes and other minor changes (fix, refactor, perf, docs, style, etc.)
* **minor**: New features (feat)
* **major**: Breaking changes (when the commit message contains "BREAKING CHANGE:")

## CI/CD Integration

Our CI/CD pipeline automatically runs python-semantic-release on the main branch after tests pass. The release process:

1. Analyzes commits since the last release
2. Determines the next version number
3. Generates release notes
4. Creates a new Git tag
5. Updates CHANGELOG.md
6. Creates a GitHub release
7. Builds and deploys the application with the new version

## Configuration

Python-semantic-release is configured in the `pyproject.toml` file with the following key settings:

```toml
[tool.semantic_release]
version_variable = "MAAMS_NG_BE/setup.py:version"
branch = "main"
upload_to_pypi = false
upload_to_release = true
build_command = false
commit_parser = "angular"
version_source = "commit"
```

The version is tracked in the `MAAMS_NG_BE/setup.py` file. 