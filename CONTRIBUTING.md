# Contributing to ETHYS CrewAI

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the ETHYS CrewAI integration.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ethys-crewai.git
   cd ethys-crewai
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We use the following tools for code quality:

- **Black** - Code formatting (line length: 100)
- **Ruff** - Linting
- **MyPy** - Type checking (permissive, not strict)

**Before committing:**
```bash
# Format code
black ethys402_crewai/ tests/ examples/

# Lint
ruff check ethys402_crewai/ tests/ examples/

# Type check
mypy ethys402_crewai/
```

### Writing Tests

- **Unit tests** - Test individual functions/methods (mocked HTTP)
- **Integration tests** - Test against real API (skip if credentials unavailable)

**Run tests:**
```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# With coverage
pytest --cov=ethys402_crewai --cov-report=term-missing
```

**Test requirements:**
- All new features must include tests
- Maintain or improve test coverage
- Tests should be fast and isolated

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes (Google style)
- Update examples if adding new features
- Update CHANGELOG.md for user-visible changes

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add ERC-6551 identity support
fix: Handle connection timeout errors
docs: Update quickstart example
test: Add tests for telemetry signing
```

Prefix with: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`

## Pull Request Process

1. **Update your fork** with the latest changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Ensure all checks pass:**
   - Tests pass
   - Linting passes
   - Type checking passes
   - Documentation updated

3. **Open a Pull Request:**
   - Clear title and description
   - Reference related issues
   - Include examples if applicable
   - Add screenshots/demos for UI changes (if any)

4. **Address feedback:**
   - Respond to review comments
   - Make requested changes
   - Update PR as needed

## Code Review Guidelines

- Be respectful and constructive
- Focus on code quality and correctness
- Ask questions if something is unclear
- Suggest improvements, don't just point out issues

## Areas for Contribution

We welcome contributions in these areas:

- **New features** - Additional protocol endpoints or capabilities
- **Bug fixes** - Issues reported or discovered
- **Documentation** - Improvements to README, examples, docstrings
- **Tests** - Additional test coverage
- **Performance** - Optimizations and improvements
- **Examples** - New use cases and workflows

## Questions?

- Open an issue for questions or discussion
- Check existing issues first
- Be patient - maintainers are volunteers

Thank you for contributing! 🚀

