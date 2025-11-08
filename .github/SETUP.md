# GitHub Actions Setup Guide

This document describes the CI/CD setup for chuk-acp and how to configure it.

## Workflows Overview

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers:** Push to main/develop, Pull Requests

**Jobs:**
- **Lint & Format Check**: Runs Black and Ruff
- **Type Check**: Runs mypy for type safety
- **Test**: Tests on Python 3.11 & 3.12 across Ubuntu, macOS, Windows
- **Test without Pydantic**: Ensures fallback compatibility
- **Build**: Builds the package and uploads artifacts

**Purpose:** Ensures all code changes pass quality checks before merging.

### 2. Publish Workflow (`.github/workflows/publish.yml`)

**Triggers:**
- Automatic: When a new GitHub Release is published
- Manual: Via workflow dispatch (for TestPyPI testing)

**Jobs:**
- **Build**: Creates distribution packages
- **Publish to TestPyPI**: Manual testing before production
- **Publish to PyPI**: Automatic on release
- **GitHub Release**: Signs packages with Sigstore

**Purpose:** Automates package publishing to PyPI.

### 3. CodeQL Security Scan (`.github/workflows/codeql.yml`)

**Triggers:** Push to main, PRs, Weekly schedule

**Purpose:** Identifies security vulnerabilities in the codebase.

### 4. Release Drafter (`.github/workflows/release-drafter.yml`)

**Triggers:** Push to main, PRs

**Purpose:** Auto-generates release notes from PRs.

## Required Secrets

### For PyPI Publishing

The publish workflow uses **Trusted Publishers** (recommended) instead of API tokens:

1. **Go to PyPI**: https://pypi.org/manage/account/publishing/
2. **Add a new publisher**:
   - PyPI Project Name: `chuk-acp`
   - Owner: `chuk-ai`
   - Repository: `chuk-acp`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`

3. **For TestPyPI** (optional): https://test.pypi.org/manage/account/publishing/
   - Follow same steps with environment name: `testpypi`

**No secrets needed!** GitHub OIDC provides the authentication.

### For Codecov (Optional)

1. Go to https://codecov.io/
2. Connect your GitHub repository
3. Get the upload token
4. Add to GitHub Secrets:
   - Name: `CODECOV_TOKEN`
   - Value: Your Codecov token

Without this, coverage reports won't upload (but CI will still pass).

## GitHub Repository Settings

### Branch Protection

Recommended settings for `main` branch:

1. **Settings** → **Branches** → **Add rule**
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
     - Required checks: `lint`, `type-check`, `test`, `build`
   - ✅ Require conversation resolution before merging
   - ✅ Do not allow bypassing the above settings

### Environments

Create environments for deployment:

1. **Settings** → **Environments** → **New environment**

**PyPI Environment:**
- Name: `pypi`
- Deployment protection rules:
  - ✅ Required reviewers (optional but recommended)
  - ✅ Wait timer: 0 minutes

**TestPyPI Environment:**
- Name: `testpypi`
- No protection rules needed

### Enable GitHub Features

1. **Settings** → **General**:
   - ✅ Issues
   - ✅ Discussions (for Q&A)
   - ✅ Allow squash merging
   - ✅ Automatically delete head branches

2. **Settings** → **Code security and analysis**:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ CodeQL analysis (via workflow)

## How to Release

### Automated Release (Recommended)

1. **Update version** in `pyproject.toml`:
   ```bash
   make bump-patch  # for 0.1.X
   make bump-minor  # for 0.X.0
   make bump-major  # for X.0.0
   ```

2. **Commit the version change**:
   ```bash
   git add pyproject.toml
   git commit -m "chore: bump version to X.Y.Z"
   git push
   ```

3. **Create and push a tag**:
   ```bash
   make publish
   # This creates a tag and triggers the automated release
   ```

4. **Monitor the workflow**:
   - Go to Actions tab
   - Watch the publish workflow
   - Verify package appears on PyPI

### Manual Release

```bash
# Build locally
make build

# Test on TestPyPI first
make publish-test

# If tests pass, publish to PyPI
make publish-manual
```

## Testing Before Release

### Test on TestPyPI

Use the workflow dispatch to publish to TestPyPI:

1. Go to **Actions** → **Publish to PyPI**
2. Click **Run workflow**
3. Select `testpypi` environment
4. Click **Run workflow**

Then test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ chuk-acp==X.Y.Z
```

## Monitoring

### CI Status

- **GitHub Actions**: All workflow runs and logs
- **Badges**: README shows real-time CI status
- **Codecov**: Coverage trends and reports

### Security

- **Dependabot**: Weekly dependency updates
- **CodeQL**: Weekly security scans
- **Sigstore**: Package signature verification

## Troubleshooting

### CI Fails on Windows

- Check line endings (CRLF vs LF)
- Verify paths use forward slashes

### PyPI Publishing Fails

1. Verify Trusted Publisher is configured correctly
2. Check environment name matches (`pypi` or `testpypi`)
3. Ensure workflow has `id-token: write` permission

### Coverage Upload Fails

- Add `CODECOV_TOKEN` to repository secrets
- Or set `fail_ci_if_error: false` in workflow

### Tests Fail Without Pydantic

- Ensure your code properly handles the `PYDANTIC_AVAILABLE` flag
- Check fallback implementations work correctly

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot)
- [CodeQL](https://codeql.github.com/)
