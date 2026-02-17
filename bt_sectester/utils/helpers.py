"""
Helper utilities for bt-sec-analyzer.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from bt_sectester.utils.logger import LoggerMixin


def validate_mac_address(mac: str) -> bool:
    """
    Validate Bluetooth MAC address format.

    Args:
        mac: MAC address string

    Returns:
        True if valid format
    """
    pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return bool(re.match(pattern, mac))


def normalize_mac_address(mac: str) -> str:
    """
    Normalize MAC address to standard format (uppercase with colons).

    Args:
        mac: MAC address string

    Returns:
        Normalized MAC address
    """
    # Remove any separators and convert to uppercase
    cleaned = mac.replace(":", "").replace("-", "").upper()

    # Add colons
    return ":".join(cleaned[i : i + 2] for i in range(0, 12, 2))


def parse_bluetooth_class(device_class: int) -> Dict[str, str]:
    """
    Parse Bluetooth device class to human-readable format.

    Args:
        device_class: Device class integer

    Returns:
        Dictionary with device type information
    """
    # Major device classes
    major_classes = {
        0x00: "Miscellaneous",
        0x01: "Computer",
        0x02: "Phone",
        0x03: "LAN/Network Access Point",
        0x04: "Audio/Video",
        0x05: "Peripheral",
        0x06: "Imaging",
        0x07: "Wearable",
        0x08: "Toy",
        0x09: "Health",
        0x1F: "Uncategorized",
    }

    major = (device_class >> 8) & 0x1F
    minor = (device_class >> 2) & 0x3F
    service = (device_class >> 13) & 0x7FF

    return {
        "major_class": major_classes.get(major, "Unknown"),
        "major_code": major,
        "minor_code": minor,
        "service_code": service,
    }


def check_tool_availability(tool_name: str, tool_path: Optional[str] = None) -> bool:
    """
    Check if an external tool is available.

    Args:
        tool_name: Name of the tool
        tool_path: Optional explicit path to tool

    Returns:
        True if tool is available
    """
    try:
        if tool_path and Path(tool_path).exists():
            return True

        result = subprocess.run(
            ["which", tool_name],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_bluetooth_adapters() -> List[Dict[str, str]]:
    """
    Get list of available Bluetooth adapters.

    Returns:
        List of adapter information dictionaries
    """
    adapters = []

    try:
        result = subprocess.run(
            ["hciconfig"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return adapters

        # Parse hciconfig output
        current_adapter = None
        for line in result.stdout.split("\n"):
            if line and not line.startswith("\t"):
                # New adapter line
                parts = line.split(":")
                if parts:
                    adapter_name = parts[0].strip()
                    current_adapter = {
                        "name": adapter_name,
                        "address": "",
                        "type": "",
                        "status": "",
                    }
                    adapters.append(current_adapter)
            elif current_adapter and line.strip():
                # Adapter details
                if "BD Address:" in line:
                    address = line.split("BD Address:")[1].split()[0].strip()
                    current_adapter["address"] = address
                elif "UP RUNNING" in line:
                    current_adapter["status"] = "up"
                elif "DOWN" in line:
                    current_adapter["status"] = "down"

    except Exception:
        pass

    return adapters


def format_rssi(rssi: int) -> str:
    """
    Format RSSI value with signal strength indicator.

    Args:
        rssi: RSSI value in dBm

    Returns:
        Formatted string with signal indicator
    """
    if rssi >= -50:
        indicator = "Excellent"
    elif rssi >= -60:
        indicator = "Good"
    elif rssi >= -70:
        indicator = "Fair"
    else:
        indicator = "Weak"

    return f"{rssi} dBm ({indicator})"


class CommandExecutor(LoggerMixin):
    """Helper class for executing external commands."""

    def execute(
        self,
        command: List[str],
        timeout: int = 30,
        capture_output: bool = True,
    ) -> Tuple[int, str, str]:
        """
        Execute a command.

        Args:
            command: Command and arguments
            timeout: Timeout in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        self.logger.debug("Executing command", command=" ".join(command))

        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
            )

            self.logger.debug(
                "Command completed",
                return_code=result.returncode,
                stdout_length=len(result.stdout) if capture_output else 0,
            )

            return (
                result.returncode,
                result.stdout if capture_output else "",
                result.stderr if capture_output else "",
            )

        except subprocess.TimeoutExpired:
            self.logger.error("Command timed out", command=" ".join(command), timeout=timeout)
            raise
        except Exception as e:
            self.logger.error("Command execution failed", command=" ".join(command), error=str(e))
            raise


def ensure_directory(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path
    """
    path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(". ")
    return sanitized or "unnamed"
