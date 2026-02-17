# Development Guide for bt-sec-analyzer

## Quick Start

### Prerequisites

- Arch Linux (primary target)
- Python 3.12+
- Bluetooth adapter (built-in or USB)
- Root/sudo access for certain operations

### Installation

1. **Clone and setup:**
   ```bash
   git clone https://github.com/mfscpayload-690/bt-sec-analyzer.git
   cd bt-sec-analyzer

   # Run installation script
   chmod +x scripts/install_arch.sh
   ./scripts/install_arch.sh
   ```

2. **Verify installation:**
   ```bash
   poetry run python scripts/setup.py
   ```

3. **Log out and back in** (for bluetooth group membership)

## Development Setup

### Poetry Environment

```bash
# Install dependencies
poetry install --with dev

# Activate shell
poetry shell

# Run application
python -m bt_sectester
```

### Running Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=bt_sectester --cov-report=html

# Specific test file
poetry run pytest bt_sectester/tests/test_config.py -v

# Only unit tests (exclude integration)
poetry run pytest -m "not integration"
```

### Code Quality

```bash
# Format code
poetry run black bt_sectester

# Sort imports
poetry run isort bt_sectester

# Lint
poetry run flake8 bt_sectester

# Type checking
poetry run mypy bt_sectester
```

## Project Structure

```
bt-sec-analyzer/
├── bt_sectester/           # Main package
│   ├── core/              # Core engine and coordinator
│   ├── modules/           # Feature modules
│   │   ├── scanning/      # Device discovery
│   │   ├── attacks/       # Attack simulations
│   │   ├── ai/            # Ollama integration
│   │   └── reporting/     # Report generation
│   ├── utils/             # Utilities
│   ├── tests/             # Unit tests
│   ├── cli.py             # CLI interface
│   └── __main__.py        # Main entry point
├── configs/               # Configuration files
├── docker/                # Container definitions
├── scripts/               # Setup and build scripts
├── docs/                  # Documentation
└── ui/                    # Frontend (future)
```

## Usage Examples

### CLI Mode

#### Scan for devices:
```bash
poetry run bt-sec-analyzer-cli scan --duration 15 --classic --ble
```

#### Enumerate services:
```bash
poetry run bt-sec-analyzer-cli enumerate AA:BB:CC:DD:EE:FF
```

#### DoS simulation:
```bash
poetry run bt-sec-analyzer-cli simulate dos AA:BB:CC:DD:EE:FF --duration 30
```

#### Generate report:
```bash
poetry run bt-sec-analyzer-cli report session_20260217_120000 --format pdf
```

### Python API

```python
from bt_sectester.core.engine import BTSecEngine
from bt_sectester.modules.attacks.attack_simulator import AttackType

# Initialize engine
engine = BTSecEngine()

# Scan for devices
devices = engine.scan_devices(duration=10, classic=True, ble=True)

# Enumerate services
services = engine.enumerate_services("AA:BB:CC:DD:EE:FF")

# Simulate attack (requires authorization!)
from bt_sectester.modules.attacks.attack_simulator import AttackSimulator

simulator = AttackSimulator(
    privilege_manager=engine.privilege_manager,
    ethical_mode=True
)

result = simulator.execute_attack(
    attack_type=AttackType.SNIFF,
    target="AA:BB:CC:DD:EE:FF",
    duration=60
)

# Generate report
from bt_sectester.modules.reporting.report_generator import ReportGenerator

generator = ReportGenerator()
report_path = generator.generate_pdf_report(engine.session_data)

# Cleanup
engine.shutdown()
```

## Advanced Features

### Ollama Integration

1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull model:**
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

3. **Use in code:**
   ```python
   from bt_sectester.modules.ai.ollama_client import OllamaClient

   client = OllamaClient()
   summary = client.summarize_logs(logs, context="DoS attack simulation")
   ```

### Containerization

```bash
# Build containers
cd docker
./build.sh

# Run main app
podman run -it --privileged --network=host bt-sec-analyzer:latest

# Run isolated Bettercap
podman run -it --privileged --network=host bt-sec-analyzer-bettercap:latest
```

### Building Standalone Executable

```bash
chmod +x scripts/build_executable.sh
./scripts/build_executable.sh

# Run
./dist/bt-sec-analyzer
```

## Configuration

Edit `configs/config.yaml` or create `configs/local_config.yaml`:

```yaml
app:
  ethical_mode: true  # Always keep true!
  debug: false

logging:
  level: "INFO"

bluetooth:
  default_adapter: "hci0"

attacks:
  require_confirmation: true
  max_duration: 300

ollama:
  enabled: true
  host: "http://localhost:11434"
  model: "qwen2.5-coder:7b"
```

## Troubleshooting

### Bluetooth adapter not found

```bash
# Check adapter
hciconfig -a

# Bring up
sudo hciconfig hci0 up

# Check service
systemctl status bluetooth
```

### Permission denied

```bash
# Add to bluetooth group
sudo usermod -aG bluetooth $USER

# Log out and back in
```

### PyBluez import error

```bash
# Install system dependencies
sudo pacman -S bluez bluez-utils libbluetooth

# Reinstall
poetry install --with dev
```

## Performance Tips

1. **Multi-threading**: Scanner runs classic/BLE in parallel by default
2. **GPU acceleration**: Ollama uses RTX 4050 automatically
3. **Memory**: Adjust `performance.max_workers` in config
4. **Logging**: Set to INFO in production, DEBUG only when needed

## Security Best Practices

1. **Always enable ethical mode** in production
2. **Enable audit logging** (`logging.audit.enabled: true`)
3. **Require confirmations** (`attacks.require_confirmation: true`)
4. **Use privilege escalation safely** (pkexec over sudo)
5. **Test only on authorized devices**

## Adding New Features

### New Attack Type

1. Add enum to `AttackType` in `attack_simulator.py`
2. Implement handler method (e.g., `_my_attack()`)
3. Add routing in `execute_attack()`
4. Write tests
5. Update documentation

### New Module

1. Create directory under `bt_sectester/modules/`
2. Add `__init__.py`
3. Implement functionality
4. Import in main package
5. Add CLI command if needed

## Resources

- [PyBluez Documentation](https://github.com/pybluez/pybluez)
- [Bleak Documentation](https://bleak.readthedocs.io/)
- [BlueZ Wiki](http://www.bluez.org/)
- [Bluetooth Security](https://www.bluetooth.com/learn-about-bluetooth/key-attributes/bluetooth-security/)

## Support

- GitHub Issues: [Report bugs and request features](https://github.com/mfscpayload-690/bt-sec-analyzer/issues)
- Discussions: [Ask questions and share ideas](https://github.com/mfscpayload-690/bt-sec-analyzer/discussions)
- Security: [GitHub Security Advisories](https://github.com/mfscpayload-690/bt-sec-analyzer/security/advisories) (for responsible disclosure)
