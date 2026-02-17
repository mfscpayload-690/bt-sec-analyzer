# Changelog

All notable changes to bt-sec-analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Tauri-based desktop UI
- Advanced MITM capabilities
- Ubertooth hardware support
- Additional Bluetooth profiles
- Real-time attack visualization

## [0.1.0] - 2026-02-17

### Added
- Initial release
- Core engine and coordinator
- Bluetooth Classic (BR/EDR) scanning via PyBluez
- BLE scanning via Bleak
- Service enumeration (SDP and GATT)
- Attack simulations:
  - DoS flooding (L2CAP)
  - Deauthentication
  - Passive sniffing
  - PIN bruteforce
- Ollama integration for AI-powered log analysis
- PDF and HTML report generation
- Structured JSON logging with audit trails
- Privilege escalation via pkexec/sudo
- CLI interface with Rich formatting
- Configuration management via YAML
- Multi-threading for concurrent operations
- Poetry-based dependency management
- Comprehensive test suite
- CI/CD pipeline with GitHub Actions
- Docker/Podman containerization
- Installation scripts for Arch Linux

### Documentation
- README with features and usage
- CONTRIBUTING guidelines
- SECURITY policy
- Development guide
- Code comments and docstrings
- MIT License

### Testing
- Unit tests for core modules
- Configuration tests
- Helper function tests
- Logger tests
- Type checking with mypy
- Code coverage tracking

### Infrastructure
- Poetry project setup
- Pre-commit hooks configuration
- GitHub Actions CI/CD
- Dockerfile for containerization
- Build scripts for standalone executables

## [0.0.1] - 2026-02-10

### Added
- Project initialization
- Basic project structure
- Initial documentation

---

## Release Notes

### v0.1.0 - Initial Release

**Highlights:**
- Production-ready Bluetooth security testing framework
- CLI interface for all core features
- Ethical safeguards and audit logging
- Professional PDF reports
- AI-powered log summarization

**Requirements:**
- Arch Linux (primary)
- Python 3.12+
- Bluetooth adapter
- Root/sudo access

**Installation:**
```bash
git clone https://github.com/mfscpayload-690/bt-sec-analyzer.git
cd bt-sec-analyzer
./scripts/install_arch.sh
```

**Quick Start:**
```bash
poetry run bt-sec-analyzer-cli scan --duration 10
poetry run bt-sec-analyzer-cli enumerate AA:BB:CC:DD:EE:FF
poetry run bt-sec-analyzer-cli simulate dos AA:BB:CC:DD:EE:FF
```

**Breaking Changes:**
- None (initial release)

**Known Issues:**
- GUI not yet implemented (CLI only)
- Some advanced attacks require additional hardware
- Limited cross-platform support

**Contributors:**
- mfscpayload-690

---

[Unreleased]: https://github.com/mfscpayload-690/bt-sec-analyzer/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mfscpayload-690/bt-sec-analyzer/releases/tag/v0.1.0
[0.0.1]: https://github.com/mfscpayload-690/bt-sec-analyzer/releases/tag/v0.0.1
