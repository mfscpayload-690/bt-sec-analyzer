# bt-sec-analyzer

**Enterprise-Grade Bluetooth Security Testing Framework**

## ⚠️ Ethical Use Disclaimer

This tool is designed **exclusively for authorized security testing, research, and educational purposes**. Users must:

- Obtain explicit written authorization before testing any Bluetooth devices
- Comply with all applicable laws and regulations (Computer Fraud and Abuse Act, GDPR, etc.)
- Use this tool only on devices you own or have permission to test
- Enable audit logging for all operations
- Not use this tool for malicious purposes, unauthorized surveillance, or harassment

**Unauthorized use of this tool may be illegal and unethical. The authors assume no liability for misuse.**

## 🎯 Features

### Core Capabilities
- **Device Discovery**: Scan for Bluetooth Classic (BR/EDR) and BLE devices
- **Service Enumeration**: Identify supported profiles (A2DP, HFP, GATT services)
- **Traffic Interception**: Passive sniffing of Bluetooth communications
- **Security Simulations**:
  - Denial-of-Service (flooding, jamming)
  - Connection takedown (deauthentication)
  - Connection hijacking and replacement
  - Man-in-the-Middle scenarios
- **AI-Powered Analysis**: Local LLM summarization of logs and captures
- **Professional Reporting**: Generate detailed PDF assessment reports

### Technical Highlights
- Multi-threaded/multi-process architecture for high performance
- Structured JSON logging with real-time UI display
- Containerized tool isolation (Podman support)
- Privilege escalation safeguards (polkit integration)
- Offline-capable (no external dependencies)
- Cross-platform support (Linux primary, Windows/macOS partial)

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, PyBluez, Bleak, asyncio
- **Frontend**: Tauri (Rust) with Svelte/React UI
- **Bluetooth Tools**: BlueZ, Bettercap, Wireshark/tshark, Btlejack
- **AI Integration**: Ollama with Qwen Coder 7B (local LLM)
- **Packaging**: Poetry, PyInstaller/Nuitka

## 📦 Installation

### Prerequisites (Arch Linux)

```bash
# System dependencies
sudo pacman -S bluez bluez-utils python python-pip poetry \
              wireshark-cli bettercap podman git

# Optional: Ubertooth for advanced sniffing
yay -S ubertooth

# Enable Bluetooth service
sudo systemctl enable bluetooth.service
sudo systemctl start bluetooth.service
```

### Setup

```bash
# Clone repository
git clone https://github.com/mfscpayload-690/bt-sec-analyzer.git
cd bt-sec-analyzer

# Install Python dependencies
poetry install

# Optional: Install PyBluez for Classic Bluetooth support (Linux only)
# Note: PyBluez has dependency conflicts with Poetry and must be installed separately
pip install pybluez  # or: poetry run pip install pybluez

# Setup Ollama (for AI features)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:7b

# Build UI (Tauri)
cd ui && npm install && npm run build

# Run setup script
poetry run python scripts/setup.py
```

## 🚀 Usage

### GUI Mode

```bash
poetry run python -m bt_sectester
```

### CLI Mode

```bash
# Scan for devices
poetry run python -m bt_sectester.cli scan --duration 10

# Enumerate services for a device
poetry run python -m bt_sectester.cli enumerate --mac AA:BB:CC:DD:EE:FF

# Run security simulation (requires authorization)
poetry run python -m bt_sectester.cli simulate dos --target AA:BB:CC:DD:EE:FF --duration 30

# Generate report
poetry run python -m bt_sectester.cli report --session session_20260217_123456
```

## 🏗️ Architecture

```
bt_sectester/
├── core/               # Core engine and coordinator
├── modules/
│   ├── scanning/       # Device discovery (PyBluez, Bleak)
│   ├── attacks/        # Security simulation logic
│   ├── reporting/      # PDF report generation
│   └── ai/             # Ollama integration for summarization
├── ui/                 # Tauri frontend
├── utils/              # Logging, privilege handling, config
└── tests/              # Unit and integration tests
```

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=bt_sectester --cov-report=html

# Run specific test suite
poetry run pytest tests/test_scanning.py
```

## 🔒 Security Features

- **Ethical Mode**: Enforces audit logging, prevents unattended execution
- **User Confirmations**: Prompts before destructive operations
- **Privilege Isolation**: Runs with minimum required permissions
- **Audit Logging**: Comprehensive logs of all actions with timestamps
- **Containerization**: Isolates risky tools in Podman containers

## 📝 Legal and Compliance

Users are responsible for compliance with relevant laws and regulations, including but not limited to:

- Computer Fraud and Abuse Act (CFAA) - USA
- Computer Misuse Act - UK
- EU Directive on Attacks against Information Systems
- GDPR (when processing personal data)
- Local telecommunications regulations

**Always obtain proper authorization before conducting security assessments.**

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow PEP8 style guidelines
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 📧 Contact

For questions, issues, or responsible disclosure of vulnerabilities:
- GitHub Issues: [github.com/mfscpayload-690/bt-sec-analyzer](https://github.com/mfscpayload-690/bt-sec-analyzer)

---

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**
