"""
Privilege escalation utilities for BT-SecTester.

Handles sudo/pkexec operations securely with user prompts.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from bt_sectester.utils.logger import LoggerMixin


class PrivilegeError(Exception):
    """Exception raised for privilege escalation errors."""

    pass


class PrivilegeManager(LoggerMixin):
    """Manager for privilege escalation operations."""

    def __init__(self, method: str = "pkexec", cache_timeout: int = 300):
        """
        Initialize privilege manager.

        Args:
            method: Elevation method (pkexec, sudo, or none)
            cache_timeout: Sudo cache timeout in seconds
        """
        self.method = method
        self.cache_timeout = cache_timeout
        self._validate_method()

    def _validate_method(self) -> None:
        """Validate that the elevation method is available."""
        if self.method == "none":
            return

        if self.method == "pkexec":
            if not shutil.which("pkexec"):
                raise PrivilegeError("pkexec not found. Install polkit.")
        elif self.method == "sudo":
            if not shutil.which("sudo"):
                raise PrivilegeError("sudo not found.")
        else:
            raise PrivilegeError(f"Invalid privilege method: {self.method}")

    def is_root(self) -> bool:
        """Check if running as root."""
        return os.geteuid() == 0

    def requires_elevation(self, command: str) -> bool:
        """
        Check if a command requires privilege elevation.

        Args:
            command: Command to check

        Returns:
            True if elevation required
        """
        # Commands that typically require root
        root_commands = [
            "hciconfig",
            "hcitool",
            "bettercap",
            "tshark",
            "btlejack",
            "spooftooph",
            "ubertooth-util",
        ]

        cmd_base = command.split()[0] if command else ""
        return any(cmd_base.endswith(rc) for rc in root_commands)

    def execute_privileged(
        self,
        command: List[str],
        prompt: Optional[str] = None,
        confirm: bool = True,
    ) -> Tuple[int, str, str]:
        """
        Execute a command with elevated privileges.

        Args:
            command: Command and arguments as list
            prompt: Custom prompt message
            confirm: Whether to show confirmation dialog

        Returns:
            Tuple of (return_code, stdout, stderr)

        Raises:
            PrivilegeError: If elevation fails
        """
        if self.is_root():
            # Already running as root
            return self._execute_command(command)

        if self.method == "none":
            # Try without elevation (may fail)
            self.logger.warning("Executing without privilege elevation", command=command)
            return self._execute_command(command)

        # Log the privileged operation
        self.logger.info(
            "Requesting privilege elevation",
            command=" ".join(command),
            method=self.method,
        )

        # Build elevated command
        if self.method == "pkexec":
            elevated_cmd = ["pkexec"] + command
        elif self.method == "sudo":
            elevated_cmd = ["sudo", "-S"] + command  # -S reads password from stdin
        else:
            raise PrivilegeError(f"Unsupported method: {self.method}")

        try:
            return self._execute_command(elevated_cmd)
        except subprocess.CalledProcessError as e:
            raise PrivilegeError(f"Privilege elevation failed: {e}") from e

    def _execute_command(self, command: List[str]) -> Tuple[int, str, str]:
        """
        Execute a command directly.

        Args:
            command: Command and arguments

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as e:
            raise PrivilegeError(f"Command timed out: {e}") from e
        except Exception as e:
            raise PrivilegeError(f"Command execution failed: {e}") from e

    def check_bluetooth_permissions(self) -> bool:
        """
        Check if user has necessary Bluetooth permissions.

        Returns:
            True if permissions are adequate
        """
        # Check if user is in bluetooth group
        try:
            result = subprocess.run(
                ["groups"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            groups = result.stdout.strip().split()
            if "bluetooth" in groups or self.is_root():
                return True

            self.logger.warning(
                "User not in bluetooth group. Some operations may require elevation."
            )
            return False
        except Exception as e:
            self.logger.error("Failed to check groups", error=str(e))
            return False

    def setup_bluetooth_permissions(self) -> None:
        """Add user to bluetooth group (requires elevation)."""
        if self.is_root():
            self.logger.error("Cannot add root user to groups")
            return

        username = os.getenv("USER", "")
        if not username:
            self.logger.error("Could not determine username")
            return

        try:
            self.logger.info(f"Adding user {username} to bluetooth group")
            self.execute_privileged(["usermod", "-aG", "bluetooth", username])
            self.logger.info(
                "Added to bluetooth group. Log out and back in for changes to take effect."
            )
        except PrivilegeError as e:
            self.logger.error("Failed to add user to bluetooth group", error=str(e))
