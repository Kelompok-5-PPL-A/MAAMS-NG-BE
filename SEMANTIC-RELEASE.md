# Semantic Versioning with Python Semantic Release

This project uses [Python Semantic Release](https://python-semantic-release.readthedocs.io/) for automated version management and package publishing. It helps enforce conventional commit messages and automatically determines the next version number based on your commit history.

## Installation

```bash
pip install python-semantic-release
```

## Using Semantic Release

### Making Commits

Follow the conventional commit format:

```bash
git commit -m "type(scope): subject"
```

This format helps semantic release determine the next version number.

### Commit Message Format

Each commit message should be structured as follows:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

Must be one of the following:

* **feat**: A new feature (triggers a minor version bump)
* **fix**: A bug fix (triggers a patch version bump)
* **perf**: A code change that improves performance (triggers a patch version bump)
* **refactor**: A code change that neither fixes a bug nor adds a feature (triggers a patch version bump)
* **docs**: Documentation only changes (no version bump)
* **style**: Changes that do not affect the meaning of the code (no version bump)
* **test**: Adding missing tests or correcting existing tests (no version bump)
* **build**: Changes that affect the build system or external dependencies (no version bump)
* **ci**: Changes to our CI configuration files and scripts (no version bump)
* **chore**: Other changes that don't modify src or test files (no version bump)
* **revert**: Reverts a previous commit (no version bump)

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
feat(auth): implement Google OAuth authentication

- Add Google OAuth provider configuration
- Create OAuth callback endpoint
- Implement token generation and validation

fix(api): resolve token refresh issue

- Fix token refresh logic in authentication service
- Add proper error handling for expired tokens
- Update token validation middleware

feat(api)!: restructure authentication endpoints

BREAKING CHANGE: Authentication endpoints have been restructured:
- /auth/login is now /api/v1/auth/login
- /auth/refresh is now /api/v1/auth/refresh
- All endpoints now require API version in path

perf(database): optimize query performance

- Add database indexes for frequently queried fields
- Implement query caching for user profiles
- Optimize JOIN operations in cause queries

refactor(services): improve code organization

- Move business logic to dedicated service classes
- Implement dependency injection pattern
- Extract common utilities to shared module

docs(api): update API documentation

- Add OpenAPI specifications for new endpoints
- Update README with setup instructions
- Add examples for common API calls

ci: update deployment workflow

- Add staging environment configuration
- Implement automated rollback on failure
- Add deployment health checks

chore: update project dependencies

- Update Django to 4.2.7
- Upgrade djangorestframework to 3.14.0
- Update development dependencies
```

## Version Bumping

Semantic Release automatically determines the next version based on commit types:

* **patch**: Bug fixes and other minor changes (fix, refactor, perf)
* **minor**: New features (feat)
* **major**: Breaking changes (when the commit message contains "BREAKING CHANGE:" or ends with "!")

To manually bump the version:

```bash
semantic-release version
```

## CI/CD Integration

Our CI/CD pipeline automatically runs Semantic Release on the main and staging branches after tests pass. The release process:

1. Analyzes commits since the last release
2. Determines the next version number
3. Generates release notes
4. Creates a new Git tag
5. Updates version in tracked files
6. Creates a GitHub release
7. Builds and deploys the application with the new version

## Configuration

Semantic Release is configured in the `pyproject.toml` file with the following key settings:

```toml
[tool.semantic_release]
version_variable = [
    "setup.py:version",
    "MAAMS_NG_BE/__init__.py:__version__"
]
branch = "main"
upload_to_repository = true
upload_to_release = true
build_command = "python setup.py sdist bdist_wheel"

major_on_zero = false
commit_parser = "angular"
commit_author = "github-actions <github-actions@github.com"

# GitHub release settings
github_repository = "your-org/MAAMS_NG_BE"
github_release = true
github_release_title = "Release {version}"

# Changelog configuration
changelog_file = "CHANGELOG.md"
changelog_scope = false
changelog_sections = [
    "breaking", 
    "feature", 
    "fix", 
    "performance", 
    "documentation", 
    "refactor"
]

[tool.semantic_release.commit_parser_options]
allowed_tags = [
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "style",
    "test"
]
minor_tags = ["feat"]
patch_tags = ["fix", "perf", "refactor"]

[tool.semantic_release.branches.main]
match = "main"
prerelease = false

[tool.semantic_release.branches.staging]
match = "staging"
prerelease = true
prerelease_token = "beta"
```

The version is tracked in both `setup.py` and `MAAMS_NG_BE/__init__.py` files.

## Best Practices

1. Always follow the conventional commit format
2. Keep commit messages clear and descriptive
3. Use appropriate commit types
4. Include scope when changes affect specific modules
5. Document breaking changes clearly
6. Reference issues when applicable
7. Use bullet points in commit body for better readability
8. Keep related changes in a single commit
9. Test changes before committing

## Troubleshooting

If you encounter issues with Semantic Release:

1. Ensure you have the latest version: `pip install --upgrade python-semantic-release`
2. Check your commit message format
3. Verify your configuration in `pyproject.toml`
4. Check the CI/CD logs for any version bumping issues
5. Ensure your GitHub token has the necessary permissions
6. Verify that the version variables in tracked files are correctly formatted 