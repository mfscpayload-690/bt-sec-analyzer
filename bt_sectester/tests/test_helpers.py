"""
Tests for utility helpers.
"""

import pytest

from bt_sectester.utils.helpers import (
    format_rssi,
    normalize_mac_address,
    parse_bluetooth_class,
    sanitize_filename,
    validate_mac_address,
)


def test_validate_mac_address():
    """Test MAC address validation."""
    # Valid formats
    assert validate_mac_address("AA:BB:CC:DD:EE:FF") is True
    assert validate_mac_address("aa:bb:cc:dd:ee:ff") is True
    assert validate_mac_address("AA-BB-CC-DD-EE-FF") is True

    # Invalid formats
    assert validate_mac_address("AABBCCDDEEFF") is False
    assert validate_mac_address("AA:BB:CC:DD:EE") is False
    assert validate_mac_address("ZZ:ZZ:ZZ:ZZ:ZZ:ZZ") is False
    assert validate_mac_address("not a mac") is False


def test_normalize_mac_address():
    """Test MAC address normalization."""
    assert normalize_mac_address("aa:bb:cc:dd:ee:ff") == "AA:BB:CC:DD:EE:FF"
    assert normalize_mac_address("AA-BB-CC-DD-EE-FF") == "AA:BB:CC:DD:EE:FF"
    assert normalize_mac_address("AABBCCDDEEFF") == "AA:BB:CC:DD:EE:FF"


def test_parse_bluetooth_class():
    """Test Bluetooth device class parsing."""
    # Example: Phone device class
    device_class = 0x5A020C
    parsed = parse_bluetooth_class(device_class)

    assert "major_class" in parsed
    assert "major_code" in parsed
    assert "minor_code" in parsed
    assert "service_code" in parsed


def test_format_rssi():
    """Test RSSI formatting."""
    assert "Excellent" in format_rssi(-40)
    assert "Good" in format_rssi(-55)
    assert "Fair" in format_rssi(-65)
    assert "Weak" in format_rssi(-85)


def test_sanitize_filename():
    """Test filename sanitization."""
    assert sanitize_filename("test<file>.txt") == "test_file_.txt"
    assert sanitize_filename("path/to/file") == "path_to_file"
    assert sanitize_filename("file:name") == "file_name"
    assert sanitize_filename("") == "unnamed"
    assert sanitize_filename("...") == "unnamed"
