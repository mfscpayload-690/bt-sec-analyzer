"""
Bluetooth device scanner for both Classic (BR/EDR) and BLE.

Provides concurrent scanning with service enumeration.
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import bluetooth
except ImportError:
    bluetooth = None

try:
    from bleak import BleakScanner
except ImportError:
    BleakScanner = None

from bt_sectester.utils.helpers import (
    normalize_mac_address,
    parse_bluetooth_class,
    validate_mac_address,
)
from bt_sectester.utils.logger import LoggerMixin
from bt_sectester.utils.privileges import PrivilegeManager


class BluetoothScanner(LoggerMixin):
    """Scanner for Bluetooth Classic and BLE devices."""

    def __init__(
        self,
        adapter: str = "hci0",
        privilege_manager: Optional[PrivilegeManager] = None,
    ):
        """
        Initialize Bluetooth scanner.

        Args:
            adapter: Bluetooth adapter to use (e.g., hci0)
            privilege_manager: Privilege manager for elevated operations
        """
        self.adapter = adapter
        self.privilege_manager = privilege_manager
        self.devices_found: Dict[str, Dict[str, Any]] = {}

        # Check library availability
        if bluetooth is None:
            self.logger.warning("PyBluez not installed. Classic Bluetooth scanning disabled.")
        if BleakScanner is None:
            self.logger.warning("Bleak not installed. BLE scanning disabled.")

        self._ensure_adapter_ready()

    def _ensure_adapter_ready(self) -> None:
        """Ensure Bluetooth adapter is up and ready."""
        try:
            # Check if adapter is up
            if self.privilege_manager:
                ret_code, stdout, stderr = self.privilege_manager.execute_privileged(
                    ["hciconfig", self.adapter, "up"],
                    confirm=False,
                )
                if ret_code == 0:
                    self.logger.info("Bluetooth adapter enabled", adapter=self.adapter)
                else:
                    self.logger.warning(
                        "Failed to enable adapter",
                        adapter=self.adapter,
                        stderr=stderr,
                    )
        except Exception as e:
            self.logger.warning("Could not verify adapter status", error=str(e))

    def scan(
        self,
        duration: int = 10,
        classic: bool = True,
        ble: bool = True,
        concurrent: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Scan for Bluetooth devices.

        Args:
            duration: Scan duration in seconds
            classic: Enable classic Bluetooth scanning
            ble: Enable BLE scanning
            concurrent: Run both scans concurrently

        Returns:
            List of discovered devices
        """
        self.devices_found.clear()
        self.logger.info(
            "Starting Bluetooth scan",
            duration=duration,
            classic=classic,
            ble=ble,
            concurrent=concurrent,
        )

        if concurrent and classic and ble:
            # Run both scans in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                classic_future = executor.submit(self._scan_classic, duration)
                ble_future = executor.submit(self._scan_ble, duration)

                classic_devices = classic_future.result()
                ble_devices = ble_future.result()
        else:
            # Run scans sequentially
            classic_devices = self._scan_classic(duration) if classic else []
            ble_devices = self._scan_ble(duration) if ble else []

        # Merge results
        all_devices = list(self.devices_found.values())

        self.logger.info(
            "Scan complete",
            total_devices=len(all_devices),
            classic_count=len(classic_devices),
            ble_count=len(ble_devices),
        )

        return all_devices

    def _scan_classic(self, duration: int) -> List[Dict[str, Any]]:
        """
        Scan for classic Bluetooth devices.

        Args:
            duration: Scan duration in seconds

        Returns:
            List of discovered classic devices
        """
        if bluetooth is None:
            self.logger.warning("PyBluez not available. Skipping classic scan.")
            return []

        self.logger.debug("Starting classic Bluetooth scan")
        devices = []

        try:
            # Discover nearby devices
            nearby_devices = bluetooth.discover_devices(
                duration=duration,
                lookup_names=True,
                lookup_class=True,
                device_id=self._get_device_id(),
            )

            for addr, name, device_class in nearby_devices:
                device_info = {
                    "mac": normalize_mac_address(addr),
                    "name": name or "Unknown",
                    "type": "classic",
                    "device_class": device_class,
                    "device_class_parsed": parse_bluetooth_class(device_class),
                    "discovered_at": datetime.utcnow().isoformat(),
                    "rssi": None,  # Classic scan doesn't provide RSSI
                }

                self.devices_found[device_info["mac"]] = device_info
                devices.append(device_info)

                self.logger.debug(
                    "Classic device discovered",
                    mac=device_info["mac"],
                    name=device_info["name"],
                )

        except OSError as e:
            self.logger.error("Classic scan failed. May require elevated privileges.", error=str(e))
        except Exception as e:
            self.logger.error("Classic scan error", error=str(e))

        self.logger.debug("Classic scan complete", device_count=len(devices))
        return devices

    def _scan_ble(self, duration: int) -> List[Dict[str, Any]]:
        """
        Scan for BLE devices.

        Args:
            duration: Scan duration in seconds

        Returns:
            List of discovered BLE devices
        """
        if BleakScanner is None:
            self.logger.warning("Bleak not available. Skipping BLE scan.")
            return []

        self.logger.debug("Starting BLE scan")
        devices = []

        try:
            # Run async scan in a new event loop (to avoid conflicts)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            devices = loop.run_until_complete(self._async_ble_scan(duration))
            loop.close()

        except Exception as e:
            self.logger.error("BLE scan error", error=str(e))

        self.logger.debug("BLE scan complete", device_count=len(devices))
        return devices

    async def _async_ble_scan(self, duration: int) -> List[Dict[str, Any]]:
        """
        Async BLE scan implementation.

        Args:
            duration: Scan duration in seconds

        Returns:
            List of discovered BLE devices
        """
        devices = []

        discovered_devices = await BleakScanner.discover(timeout=duration)

        for device in discovered_devices:
            device_info = {
                "mac": normalize_mac_address(device.address),
                "name": device.name or "Unknown",
                "type": "ble",
                "rssi": device.rssi,
                "discovered_at": datetime.utcnow().isoformat(),
                "metadata": device.metadata,
            }

            # Avoid duplicates (in case device found in both scans)
            mac = device_info["mac"]
            if mac in self.devices_found:
                # Merge information
                self.devices_found[mac]["type"] = "classic+ble"
                self.devices_found[mac]["rssi"] = device_info["rssi"]
                self.devices_found[mac]["ble_metadata"] = device_info["metadata"]
            else:
                self.devices_found[mac] = device_info
                devices.append(device_info)

            self.logger.debug(
                "BLE device discovered",
                mac=device_info["mac"],
                name=device_info["name"],
                rssi=device_info["rssi"],
            )

        return devices

    def _get_device_id(self) -> int:
        """
        Get device ID from adapter name.

        Returns:
            Device ID (e.g., 0 for hci0)
        """
        try:
            return int(self.adapter.replace("hci", ""))
        except ValueError:
            return 0

    def enumerate_services(self, mac_address: str) -> Dict[str, Any]:
        """
        Enumerate services for a specific device.

        Args:
            mac_address: Target device MAC address

        Returns:
            Dictionary with service information
        """
        if not validate_mac_address(mac_address):
            raise ValueError(f"Invalid MAC address: {mac_address}")

        mac = normalize_mac_address(mac_address)
        self.logger.info("Enumerating services", mac=mac)

        # Determine device type
        device = self.devices_found.get(mac)
        if not device:
            # Try a quick scan to find the device
            self.logger.debug("Device not in cache, performing rescan")
            self.scan(duration=5)
            device = self.devices_found.get(mac)

        if not device:
            raise ValueError(f"Device not found: {mac}")

        device_type = device.get("type", "unknown")

        if "classic" in device_type:
            return self._enumerate_classic_services(mac)
        elif device_type == "ble":
            return self._enumerate_ble_services(mac)
        else:
            raise ValueError(f"Unknown device type: {device_type}")

    def _enumerate_classic_services(self, mac: str) -> Dict[str, Any]:
        """
        Enumerate classic Bluetooth services (SDP).

        Args:
            mac: Device MAC address

        Returns:
            Service information
        """
        if bluetooth is None:
            raise RuntimeError("PyBluez not available")

        self.logger.debug("Enumerating classic services", mac=mac)

        try:
            services = bluetooth.find_service(address=mac)

            service_list = []
            for service in services:
                service_info = {
                    "name": service.get("name", "Unknown"),
                    "description": service.get("description", ""),
                    "protocol": service.get("protocol", ""),
                    "port": service.get("port"),
                    "service_id": service.get("service-id", ""),
                    "profile": service.get("profiles", []),
                    "host": service.get("host", ""),
                }
                service_list.append(service_info)

            result = {
                "mac": mac,
                "type": "classic",
                "services": service_list,
                "service_count": len(service_list),
                "enumerated_at": datetime.utcnow().isoformat(),
            }

            self.logger.info(
                "Classic services enumerated",
                mac=mac,
                service_count=len(service_list),
            )

            return result

        except Exception as e:
            self.logger.error("Failed to enumerate classic services", mac=mac, error=str(e))
            raise

    def _enumerate_ble_services(self, mac: str) -> Dict[str, Any]:
        """
        Enumerate BLE services (GATT).

        Args:
            mac: Device MAC address

        Returns:
            Service information
        """
        if BleakScanner is None:
            raise RuntimeError("Bleak not available")

        self.logger.debug("Enumerating BLE services", mac=mac)

        try:
            # Run async enumeration
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._async_enumerate_ble(mac))
            loop.close()
            return result

        except Exception as e:
            self.logger.error("Failed to enumerate BLE services", mac=mac, error=str(e))
            raise

    async def _async_enumerate_ble(self, mac: str) -> Dict[str, Any]:
        """
        Async BLE service enumeration.

        Args:
            mac: Device MAC address

        Returns:
            Service information
        """
        from bleak import BleakClient

        service_list = []

        async with BleakClient(mac) as client:
            if not client.is_connected:
                raise ConnectionError(f"Failed to connect to {mac}")

            # Get all services
            services = client.services

            for service in services:
                service_info = {
                    "uuid": str(service.uuid),
                    "description": service.description,
                    "characteristics": [],
                }

                # Get characteristics for each service
                for char in service.characteristics:
                    char_info = {
                        "uuid": str(char.uuid),
                        "description": char.description,
                        "properties": char.properties,
                    }
                    service_info["characteristics"].append(char_info)

                service_list.append(service_info)

        result = {
            "mac": mac,
            "type": "ble",
            "services": service_list,
            "service_count": len(service_list),
            "enumerated_at": datetime.utcnow().isoformat(),
        }

        self.logger.info(
            "BLE services enumerated",
            mac=mac,
            service_count=len(service_list),
        )

        return result
