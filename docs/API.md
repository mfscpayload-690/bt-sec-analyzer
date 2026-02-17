# API Reference

## Core Engine

### BTSecEngine

Main engine coordinating all BT-SecTester operations.

```python
from bt_sectester.core.engine import BTSecEngine

engine = BTSecEngine(config=None)
```

#### Methods

##### `scan_devices(duration, classic, ble)`
Scan for Bluetooth devices.

- **Parameters:**
  - `duration` (int, optional): Scan duration in seconds
  - `classic` (bool): Scan for classic Bluetooth
  - `ble` (bool): Scan for BLE devices
- **Returns:** List of device dictionaries
- **Example:**
  ```python
  devices = engine.scan_devices(duration=10, classic=True, ble=True)
  ```

##### `enumerate_services(mac_address)`
Enumerate services for a device.

- **Parameters:**
  - `mac_address` (str): Target MAC address
- **Returns:** Service information dictionary
- **Example:**
  ```python
  services = engine.enumerate_services("AA:BB:CC:DD:EE:FF")
  ```

##### `save_session(filepath)`
Save current session data.

- **Parameters:**
  - `filepath` (Path, optional): Output path
- **Returns:** Path to saved session
- **Example:**
  ```python
  path = engine.save_session()
  ```

##### `shutdown()`
Gracefully shutdown the engine.

- **Example:**
  ```python
  engine.shutdown()
  ```

---

## Bluetooth Scanner

### BluetoothScanner

Scanner for Bluetooth Classic and BLE devices.

```python
from bt_sectester.modules.scanning.bluetooth_scanner import BluetoothScanner

scanner = BluetoothScanner(adapter="hci0", privilege_manager=None)
```

#### Methods

##### `scan(duration, classic, ble, concurrent)`
Scan for devices.

- **Parameters:**
  - `duration` (int): Scan duration
  - `classic` (bool): Enable classic scan
  - `ble` (bool): Enable BLE scan
  - `concurrent` (bool): Run both scans in parallel
- **Returns:** List of devices

##### `enumerate_services(mac_address)`
Enumerate services for a device.

- **Parameters:**
  - `mac_address` (str): Target MAC
- **Returns:** Service dictionary

---

## Attack Simulator

### AttackSimulator

Simulator for Bluetooth attacks.

```python
from bt_sectester.modules.attacks.attack_simulator import AttackSimulator, AttackType

simulator = AttackSimulator(
    privilege_manager=privilege_mgr,
    ethical_mode=True,
    require_confirmation=True
)
```

#### Attack Types

```python
class AttackType(Enum):
    DOS_FLOOD = "dos_flood"
    DOS_JAM = "dos_jam"
    DEAUTH = "deauthentication"
    HIJACK = "hijacking"
    PIN_BRUTE = "pin_bruteforce"
    MITM = "man_in_the_middle"
    SNIFF = "passive_sniffing"
```

#### Methods

##### `execute_attack(attack_type, target, duration, parameters, callback)`
Execute an attack simulation.

- **Parameters:**
  - `attack_type` (AttackType): Type of attack
  - `target` (str): Target MAC address
  - `duration` (int, optional): Duration in seconds
  - `parameters` (dict, optional): Attack parameters
  - `callback` (callable, optional): Progress callback
- **Returns:** AttackResult object
- **Example:**
  ```python
  result = simulator.execute_attack(
      attack_type=AttackType.DOS_FLOOD,
      target="AA:BB:CC:DD:EE:FF",
      duration=30
  )
  ```

##### `stop_attack(attack_id)`
Stop a running attack.

- **Parameters:**
  - `attack_id` (str): Attack identifier
- **Returns:** bool (success)

---

## AI Integration

### OllamaClient

Client for Ollama local LLM.

```python
from bt_sectester.modules.ai.ollama_client import OllamaClient

client = OllamaClient(
    host="http://localhost:11434",
    model="qwen2.5-coder:7b",
    timeout=60
)
```

#### Methods

##### `summarize_logs(logs, context)`
Summarize log entries.

- **Parameters:**
  - `logs` (list): List of log dictionaries
  - `context` (str, optional): Context for summarization
- **Returns:** Summary string
- **Example:**
  ```python
  summary = client.summarize_logs(logs, context="DoS attack")
  ```

##### `analyze_attack_results(attack_type, results)`
Analyze attack results.

- **Parameters:**
  - `attack_type` (str): Attack type
  - `results` (dict): Results dictionary
- **Returns:** Analysis string

##### `extract_key_insights(text, max_insights)`
Extract key insights from text.

- **Parameters:**
  - `text` (str): Input text
  - `max_insights` (int): Maximum insights to extract
- **Returns:** List of insight strings

---

## Report Generator

### ReportGenerator

Generator for security reports.

```python
from bt_sectester.modules.reporting.report_generator import ReportGenerator

generator = ReportGenerator(
    output_dir=Path("reports"),
    company_name="Security Assessment"
)
```

#### Methods

##### `generate_pdf_report(session_data, output_filename, include_raw_logs, ai_summary)`
Generate PDF report.

- **Parameters:**
  - `session_data` (dict): Session data
  - `output_filename` (str, optional): Output filename
  - `include_raw_logs` (bool): Include raw logs
  - `ai_summary` (str, optional): AI summary
- **Returns:** Path to report
- **Example:**
  ```python
  report = generator.generate_pdf_report(
      session_data=session_data,
      ai_summary="Summary text"
  )
  ```

##### `generate_html_report(session_data, output_filename)`
Generate HTML report.

- **Parameters:**
  - `session_data` (dict): Session data
  - `output_filename` (str, optional): Output filename
- **Returns:** Path to report

---

## Configuration

### Config

Configuration management.

```python
from bt_sectester.utils.config import Config

config = Config.load("configs/config.yaml")
```

#### Methods

##### `load(config_path)`
Load configuration from file.

- **Parameters:**
  - `config_path` (str, optional): Path to config file
- **Returns:** Config instance

##### `get(key, default)`
Get configuration value.

- **Parameters:**
  - `key` (str): Dot notation key (e.g., "logging.level")
  - `default` (any, optional): Default value
- **Returns:** Configuration value

##### `set(key, value)`
Set configuration value.

- **Parameters:**
  - `key` (str): Dot notation key
  - `value` (any): Value to set

##### `save(output_path)`
Save configuration to file.

- **Parameters:**
  - `output_path` (str, optional): Output path

---

## Utilities

### Helper Functions

```python
from bt_sectester.utils.helpers import (
    validate_mac_address,
    normalize_mac_address,
    parse_bluetooth_class,
    format_rssi,
    sanitize_filename
)
```

#### `validate_mac_address(mac)`
Validate MAC address format.

- **Parameters:** `mac` (str)
- **Returns:** bool

#### `normalize_mac_address(mac)`
Normalize MAC to uppercase with colons.

- **Parameters:** `mac` (str)
- **Returns:** str

#### `parse_bluetooth_class(device_class)`
Parse device class to readable format.

- **Parameters:** `device_class` (int)
- **Returns:** dict

#### `format_rssi(rssi)`
Format RSSI with signal indicator.

- **Parameters:** `rssi` (int)
- **Returns:** str

---

## Logging

### Setup Logger

```python
from bt_sectester.utils.logger import setup_logger, get_logger

logger = setup_logger(
    name="my_logger",
    level="INFO",
    log_format="json",
    log_file=Path("logs/app.log"),
    console=True
)

# Or get existing logger
logger = get_logger("module_name")
```

### Audit Logger

```python
from bt_sectester.utils.logger import AuditLogger

audit = AuditLogger(Path("logs/audit.json"))
audit.log_action(
    action="scan_started",
    details={"duration": 10},
    user="username",
    ethical_mode=True
)
```

---

## Error Handling

### PrivilegeError

```python
from bt_sectester.utils.privileges import PrivilegeError

try:
    # Privileged operation
    pass
except PrivilegeError as e:
    print(f"Privilege error: {e}")
```

---

## Example: Complete Workflow

```python
from bt_sectester.core.engine import BTSecEngine
from bt_sectester.modules.attacks.attack_simulator import AttackType
from bt_sectester.modules.reporting.report_generator import ReportGenerator

# Initialize
engine = BTSecEngine()

# Scan
devices = engine.scan_devices(duration=10)
print(f"Found {len(devices)} devices")

# Enumerate
if devices:
    target = devices[0]["mac"]
    services = engine.enumerate_services(target)

    # Attack (with authorization!)
    from bt_sectester.modules.attacks.attack_simulator import AttackSimulator

    simulator = AttackSimulator(
        privilege_manager=engine.privilege_manager,
        ethical_mode=True
    )

    result = simulator.execute_attack(
        attack_type=AttackType.SNIFF,
        target=target,
        duration=30
    )

    engine.session_data["attacks"].append(result.to_dict())

# Generate report
generator = ReportGenerator()
report = generator.generate_pdf_report(engine.session_data)
print(f"Report: {report}")

# Cleanup
engine.shutdown()
```
