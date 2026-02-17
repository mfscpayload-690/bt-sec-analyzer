# Contributing to BT-SecTester

Thank you for your interest in contributing to BT-SecTester! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and professional
- This is a security tool - prioritize ethical use
- Report security vulnerabilities responsibly
- Follow Python best practices (PEP 8)

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/bt-sectester.git
   cd bt-sectester
   ```

3. Install dependencies:
   ```bash
   poetry install --with dev
   ```

4. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We follow PEP 8 with Black formatting:

```bash
# Format code
poetry run black bt_sectester

# Sort imports
poetry run isort bt_sectester

# Lint
poetry run flake8 bt_sectester --max-line-length=100
```

### Type Checking

We use type hints and mypy:

```bash
poetry run mypy bt_sectester --ignore-missing-imports
```

### Testing

Write tests for new features:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=bt_sectester --cov-report=html

# Run specific test
poetry run pytest bt_sectester/tests/test_config.py
```

### Commit Messages

Follow conventional commits:

```
feat: Add new DoS attack simulation
fix: Resolve MAC address validation bug
docs: Update installation instructions
test: Add tests for Bluetooth scanner
refactor: Improve privilege manager error handling
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add yourself to CONTRIBUTORS.md
4. Submit PR with clear description:
   - What does it do?
   - Why is it needed?
   - How does it work?
   - Any breaking changes?

## Areas for Contribution

### High Priority
- UI implementation (Tauri/Electron)
- Additional attack simulations
- Hardware support (Ubertooth, etc.)
- Documentation improvements

### Medium Priority
- Performance optimizations
- Additional Bluetooth protocols
- Report template customization
- Cross-platform support (Windows, macOS)

### Low Priority
- Additional export formats
- Plugin system
- Internationalization (i18n)

## Security Considerations

When contributing attack simulations or security features:

1. **Ethical safeguards first**: Always implement authorization checks
2. **Audit logging**: Log all security-sensitive operations
3. **User confirmation**: Require explicit confirmation for destructive actions
4. **Documentation**: Clearly document legal implications
5. **Testing**: Test only on authorized devices

## Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead, email: security@example.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Questions?

- Open a discussion on GitHub
- Check existing issues and PRs
- Read the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make BT-SecTester better!
