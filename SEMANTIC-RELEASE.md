# Semantic Versioning with Commitizen

This project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) for automated version management and package publishing. Commitizen helps enforce conventional commit messages and automatically determines the next version number based on your commit history.

## Installation

```bash
pip install commitizen
```

## Using Commitizen

### Making Commits

Instead of using `git commit`, use the Commitizen CLI:

```bash
cz commit
```

This will guide you through creating a conventional commit message by asking:
1. Type of change
2. Scope of the change
3. Short description
4. Longer description (optional)
5. Breaking changes (optional)
6. Issue references (optional)

### Commit Message Format

Commitizen uses the [Conventional Commits](https://www.conventionalcommits.org/) specification. Each commit message should be structured as follows:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

Must be one of the following:

* **feat**: A new feature (triggers a minor version bump)
* **fix**: A bug fix (triggers a patch version bump)
* **docs**: Documentation only changes
* **style**: Changes that do not affect the meaning of the code
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

Just as in the subject, use the imperative, present tense. The body should include the motivation for the change and contrast this with previous behavior.

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

## Version Bumping

Commitizen automatically determines the next version based on commit types:

* **patch**: Bug fixes and other minor changes (fix, refactor, perf, docs, style, etc.)
* **minor**: New features (feat)
* **major**: Breaking changes (when the commit message contains "BREAKING CHANGE:")

To manually bump the version:

```bash
cz bump
```

## CI/CD Integration

Our CI/CD pipeline automatically runs Commitizen on the main branch after tests pass. The release process:

1. Analyzes commits since the last release
2. Determines the next version number
3. Generates release notes
4. Creates a new Git tag
5. Updates CHANGELOG.md
6. Creates a GitHub release
7. Builds and deploys the application with the new version

## Configuration

Commitizen is configured in the `pyproject.toml` file with the following key settings:

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
tag_format = "v$version"
version_files = [
    "setup.py:version",
    "MAAMS_NG_BE/__init__.py:__version__"
]
bump_message = "bump: version $current_version → $new_version [skip ci]"
update_changelog_on_bump = true
changelog_incremental = true
changelog_start_rev = "v0.1.0"
```

The version is tracked in both `setup.py` and `MAAMS_NG_BE/__init__.py` files.

## Best Practices

1. Always use `cz commit` instead of `git commit`
2. Keep commit messages clear and descriptive
3. Use appropriate commit types
4. Include scope when changes affect specific modules
5. Document breaking changes clearly
6. Reference issues when applicable

## Troubleshooting

If you encounter issues with Commitizen:

1. Ensure you have the latest version: `pip install --upgrade commitizen`
2. Check your commit message format
3. Verify your configuration in `pyproject.toml`
4. Check the CI/CD logs for any version bumping issues 