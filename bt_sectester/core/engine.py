"""
Main engine/coordinator for bt-sec-analyzer.

Orchestrates scanning, attacks, reporting, and UI interactions.
"""

import signal
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from bt_sectester.modules.ai.ollama_client import OllamaClient
from bt_sectester.modules.scanning.bluetooth_scanner import BluetoothScanner
from bt_sectester.utils.config import Config
from bt_sectester.utils.helpers import ensure_directory
from bt_sectester.utils.logger import AuditLogger, LoggerMixin, setup_logger
from bt_sectester.utils.privileges import PrivilegeManager


class BTSecEngine(LoggerMixin):
    """Main engine coordinating all bt-sec-analyzer operations."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize bt-sec-analyzer engine.

        Args:
            config: Configuration object (loads default if None)
        """
        self.config = config or Config.load()
        self._setup_logging()
        self._setup_directories()
        self._setup_components()
        self._setup_signal_handlers()

        self.session_id = self._generate_session_id()
        self.session_data: Dict[str, Any] = {
            "session_id": self.session_id,
            "start_time": datetime.utcnow().isoformat(),
            "devices": [],
            "attacks": [],
            "logs": [],
        }

        self.logger.info(
            "bt-sec-analyzer engine initialized",
            session_id=self.session_id,
            ethical_mode=self.config.app.ethical_mode,
        )

        # Log to audit trail
        self.audit_logger.log_action(
            "engine_initialized",
            details={"session_id": self.session_id},
            ethical_mode=self.config.app.ethical_mode,
        )

    def _setup_logging(self) -> None:
        """Setup logging system."""
        log_config = self.config.logging

        log_file = None
        if log_config.output.get("file", False):
            log_file = Path(log_config.output.get("file_path", "logs/bt_sectester.log"))

        setup_logger(
            name="bt_sectester",
            level=log_config.level,
            log_format=log_config.format,
            log_file=log_file,
            console=log_config.output.get("console", True),
        )

        # Setup audit logger
        if log_config.audit.get("enabled", True):
            audit_file = Path(log_config.audit.get("file_path", "logs/audit.json"))
            self.audit_logger = AuditLogger(audit_file)
        else:
            self.audit_logger = None

    def _setup_directories(self) -> None:
        """Create necessary directories."""
        directories = [
            "logs",
            "reports",
            "sessions",
            "captures",
        ]

        for directory in directories:
            ensure_directory(Path(directory))

    def _setup_components(self) -> None:
        """Initialize core components."""
        # Privilege manager
        self.privilege_manager = PrivilegeManager(
            method=self.config.privileges.get("method", "pkexec"),
            cache_timeout=self.config.privileges.get("cache_timeout", 300),
        )

        # Check Bluetooth permissions
        self.privilege_manager.check_bluetooth_permissions()

        # Thread and process pools
        max_workers = self.config.performance.get("max_workers", 8)
        max_processes = self.config.performance.get("max_processes", 4)

        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_processes)

        # Scanner
        self.scanner = BluetoothScanner(
            adapter=self.config.bluetooth.default_adapter,
            privilege_manager=self.privilege_manager,
        )

        # Ollama client (if enabled)
        if self.config.ollama.enabled:
            try:
                self.ollama_client = OllamaClient(
                    host=self.config.ollama.host,
                    model=self.config.ollama.model,
                    timeout=self.config.ollama.timeout,
                )
                self.logger.info("Ollama client initialized")
            except Exception as e:
                self.logger.warning("Failed to initialize Ollama client", error=str(e))
                self.ollama_client = None
        else:
            self.ollama_client = None

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """
        Handle shutdown signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.logger.warning("Received shutdown signal", signal=signum)
        self.shutdown()
        sys.exit(0)

    def _generate_session_id(self) -> str:
        """
        Generate unique session ID.

        Returns:
            Session ID string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"

    def scan_devices(
        self,
        duration: Optional[int] = None,
        classic: bool = True,
        ble: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Scan for Bluetooth devices.

        Args:
            duration: Scan duration in seconds
            classic: Scan for classic Bluetooth devices
            ble: Scan for BLE devices

        Returns:
            List of discovered devices
        """
        self.logger.info("Starting device scan", classic=classic, ble=ble, duration=duration)

        self.audit_logger.log_action(
            "scan_started",
            details={"classic": classic, "ble": ble, "duration": duration},
            ethical_mode=self.config.app.ethical_mode,
        )

        try:
            devices = self.scanner.scan(
                duration=duration or self.config.bluetooth.scan_duration,
                classic=classic,
                ble=ble,
            )

            self.session_data["devices"].extend(devices)

            self.logger.info("Scan completed", device_count=len(devices))

            self.audit_logger.log_action(
                "scan_completed",
                details={"device_count": len(devices)},
                ethical_mode=self.config.app.ethical_mode,
            )

            return devices

        except Exception as e:
            self.logger.error("Scan failed", error=str(e))
            raise

    def enumerate_services(self, mac_address: str) -> Dict[str, Any]:
        """
        Enumerate services for a specific device.

        Args:
            mac_address: Target device MAC address

        Returns:
            Service information dictionary
        """
        self.logger.info("Enumerating services", mac=mac_address)

        self.audit_logger.log_action(
            "enumerate_services",
            details={"mac": mac_address},
            ethical_mode=self.config.app.ethical_mode,
        )

        try:
            services = self.scanner.enumerate_services(mac_address)

            self.logger.info("Service enumeration completed", mac=mac_address, service_count=len(services.get("services", [])))

            return services

        except Exception as e:
            self.logger.error("Service enumeration failed", mac=mac_address, error=str(e))
            raise

    def save_session(self, filepath: Optional[Path] = None) -> Path:
        """
        Save current session data.

        Args:
            filepath: Optional custom save path

        Returns:
            Path to saved session file
        """
        if filepath is None:
            filepath = Path("sessions") / f"{self.session_id}.json"

        ensure_directory(filepath.parent)

        import json

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.session_data, f, indent=2)

        self.logger.info("Session saved", filepath=str(filepath))
        return filepath

    def shutdown(self) -> None:
        """Gracefully shutdown the engine."""
        self.logger.info("Shutting down bt-sec-analyzer engine")

        # Save session
        try:
            self.save_session()
        except Exception as e:
            self.logger.error("Failed to save session", error=str(e))

        # Shutdown thread and process pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)

        # Log audit entry
        if self.audit_logger:
            self.audit_logger.log_action(
                "engine_shutdown",
                details={"session_id": self.session_id},
                ethical_mode=self.config.app.ethical_mode,
            )

        self.logger.info("Shutdown complete")
