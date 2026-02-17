"""Test package initialization."""

import pytest

# Configure pytest for bt-sec-analyzer tests
pytest_plugins = []


@pytest.fixture
def mock_bluetooth():
    """Mock Bluetooth operations for testing."""

    class MockBluetooth:
        """Mock Bluetooth class."""

        @staticmethod
        def discover_devices(**kwargs):
            """Mock device discovery."""
            return [
                ("AA:BB:CC:DD:EE:FF", "Test Device 1", 0x5A020C),
                ("11:22:33:44:55:66", "Test Device 2", 0x200408),
            ]

        @staticmethod
        def find_service(address=None, **kwargs):
            """Mock service discovery."""
            return [
                {
                    "name": "Test Service",
                    "protocol": "RFCOMM",
                    "port": 1,
                    "service-id": "test-uuid",
                }
            ]

    return MockBluetooth()
