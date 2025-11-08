# Contributing to chuk-acp

Thank you for considering contributing to chuk-acp! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/chuk-ai/chuk-acp.git
cd chuk-acp
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev,pydantic]"
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/chuk_acp --cov-report=term --cov-report=html

# Run specific test file
uv run pytest tests/test_protocol_compliance.py

# Run tests without Pydantic (to test fallback behavior)
uv pip uninstall pydantic
uv run pytest
```

### Code Quality Checks

```bash
# Format code with Black
uv run black .

# Lint with Ruff
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Type checking with mypy
uv run mypy src/chuk_acp

# Security scanning with Bandit
uv run bandit -r src/chuk_acp -ll

# Run all checks at once
make check
```

### Code Style

- **Line Length**: 100 characters
- **Python Version**: Target Python 3.11+
- **Formatting**: Use Black for code formatting
- **Linting**: Use Ruff for linting
- **Type Hints**: All functions should have type hints
- **Docstrings**: Use Google-style docstrings for public APIs

## Pull Request Process

### Before Submitting

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Add tests** for new functionality

4. **Run all checks**:
   ```bash
   black .
   ruff check .
   mypy src/chuk_acp
   pytest
   ```

5. **Update documentation** if needed

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test changes
   - `refactor:` for refactoring
   - `ci:` for CI/CD changes
   - `deps:` for dependency updates

### Submitting the PR

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub

3. **Add appropriate labels**:
   - `feature` for new features
   - `fix` for bug fixes
   - `documentation` for docs
   - `breaking` for breaking changes

4. **Wait for CI checks** to pass

5. **Address review feedback** if any

### CI/CD Pipeline

All pull requests trigger the following checks:

- **Linting & Formatting**: Black, Ruff, Bandit
- **Type Checking**: mypy
- **Tests**: pytest on Python 3.11 and 3.12, across Ubuntu, macOS, and Windows
- **Tests without Pydantic**: Ensures fallback compatibility
- **CodeQL Security Scan**: Identifies potential security issues
- **Build Check**: Ensures the package builds correctly

## Release Process

### For Maintainers

1. **Update version** in `pyproject.toml`

2. **Create a new release** on GitHub:
   - Tag format: `vX.Y.Z` (e.g., `v0.1.0`)
   - Use the Release Drafter to generate release notes
   - Publish the release

3. **Automated publishing**:
   - The `publish.yml` workflow automatically publishes to PyPI on release
   - Artifacts are signed with Sigstore
   - Distributions are attached to the GitHub release

### Manual Publishing

To publish to TestPyPI for testing:

```bash
# Via GitHub Actions
# Go to Actions → Publish to PyPI → Run workflow → Select testpypi

# Or manually
python -m build
twine upload --repository testpypi dist/*
```

## Testing Protocol Compliance

The ACP specification is our source of truth. All changes must maintain compliance:

```bash
# Run protocol compliance tests
uv run pytest tests/test_protocol_compliance.py -v

# Verify all required methods are implemented
# Check that JSON-RPC 2.0 format is maintained
# Ensure content types follow the spec
```

## Architecture Guidelines

### Project Structure

```
chuk-acp/
├── src/chuk_acp/
│   ├── protocol/           # Protocol layer (JSON-RPC, messages, types)
│   ├── transport/          # Transport layer (stdio, future: websocket)
│   ├── agent.py            # High-level agent implementation
│   └── client.py           # High-level client implementation
├── tests/                  # Test suite
├── examples/               # Example implementations
└── .github/                # GitHub Actions workflows
```

### Design Principles

1. **Protocol First**: Follow ACP spec strictly
2. **Type Safety**: Use type hints everywhere
3. **Optional Pydantic**: Support both with and without Pydantic
4. **Async-First**: Use anyio for async operations
5. **Extensibility**: Allow custom methods and _meta fields
6. **Testability**: Keep components loosely coupled

## Getting Help

- **Issues**: Open an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Spec**: Refer to [ACP Specification](https://agentclientprotocol.com)

## License

By contributing to chuk-acp, you agree that your contributions will be licensed under the Apache-2.0 license.
