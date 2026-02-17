"""
Tests for configuration management.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from bt_sectester.utils.config import Config


def test_config_load_default():
    """Test loading default configuration."""
    config = Config()

    assert config.app.name == "bt-sec-analyzer"
    assert config.app.ethical_mode is True
    assert config.logging.level == "INFO"


def test_config_load_from_file():
    """Test loading configuration from YAML file."""
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config_data = {
            "app": {"name": "Test", "version": "1.0.0", "debug": True, "ethical_mode": False},
            "logging": {"level": "DEBUG", "format": "text"},
        }
        yaml.dump(config_data, f)
        temp_path = f.name

    try:
        config = Config.load(temp_path)

        assert config.app.name == "Test"
        assert config.app.version == "1.0.0"
        assert config.app.debug is True
        assert config.app.ethical_mode is False
        assert config.logging.level == "DEBUG"
    finally:
        Path(temp_path).unlink()


def test_config_get():
    """Test getting configuration values."""
    config = Config()

    assert config.get("app.name") == "bt-sec-analyzer"
    assert config.get("logging.level") == "INFO"
    assert config.get("nonexistent.key", "default") == "default"


def test_config_set():
    """Test setting configuration values."""
    config = Config()

    config.set("app.debug", True)
    assert config.app.debug is True

    config.set("logging.level", "DEBUG")
    assert config.logging.level == "DEBUG"


def test_config_validation():
    """Test configuration validation."""
    # Test invalid log level
    with pytest.raises(ValueError):
        Config(logging={"level": "INVALID"})


def test_config_save():
    """Test saving configuration to file."""
    config = Config()
    config.set("app.debug", True)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_path = f.name

    try:
        config.save(temp_path)

        # Load saved config
        loaded_config = Config.load(temp_path)
        assert loaded_config.app.debug is True
    finally:
        Path(temp_path).unlink()
