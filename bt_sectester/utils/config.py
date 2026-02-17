"""
Configuration management for BT-SecTester.

Handles loading, validation, and access to configuration settings.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class AppConfig(BaseModel):
    """Application-level configuration."""

    name: str = "BT-SecTester"
    version: str = "0.1.0"
    debug: bool = False
    ethical_mode: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "json"
    output: Dict[str, Any] = Field(default_factory=dict)
    audit: Dict[str, Any] = Field(default_factory=dict)

    @validator("level")
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()


class BluetoothConfig(BaseModel):
    """Bluetooth adapter configuration."""

    default_adapter: str = "hci0"
    scan_duration: int = 10
    classic_enabled: bool = True
    ble_enabled: bool = True
    auto_detect_adapters: bool = True


class AttacksConfig(BaseModel):
    """Attack simulation configuration."""

    require_confirmation: bool = True
    max_duration: int = 300
    dos: Dict[str, Any] = Field(default_factory=dict)
    hijack: Dict[str, Any] = Field(default_factory=dict)
    mitm: Dict[str, Any] = Field(default_factory=dict)


class OllamaConfig(BaseModel):
    """Ollama AI configuration."""

    enabled: bool = True
    host: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:7b"
    timeout: int = 60
    summarization: Dict[str, Any] = Field(default_factory=dict)


class Config(BaseSettings):
    """Main configuration class."""

    app: AppConfig = Field(default_factory=AppConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    bluetooth: BluetoothConfig = Field(default_factory=BluetoothConfig)
    attacks: AttacksConfig = Field(default_factory=AttacksConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    performance: Dict[str, Any] = Field(default_factory=dict)
    tools: Dict[str, Any] = Field(default_factory=dict)
    privileges: Dict[str, Any] = Field(default_factory=dict)
    reporting: Dict[str, Any] = Field(default_factory=dict)
    scanning: Dict[str, Any] = Field(default_factory=dict)
    session: Dict[str, Any] = Field(default_factory=dict)
    ui: Dict[str, Any] = Field(default_factory=dict)

    _instance: Optional["Config"] = None
    _config_path: Optional[Path] = None

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to configuration file. Defaults to configs/config.yaml

        Returns:
            Config instance
        """
        if cls._instance is not None:
            return cls._instance

        if config_path is None:
            # Try to find config file
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "configs" / "config.yaml"
            local_config = base_dir / "configs" / "local_config.yaml"

            # Use local config if it exists
            if local_config.exists():
                config_path = local_config

        config_file = Path(config_path)
        if not config_file.exists():
            # Return default config
            cls._instance = cls()
            return cls._instance

        with open(config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        cls._instance = cls(**config_data)
        cls._config_path = config_file
        return cls._instance

    @classmethod
    def get_instance(cls) -> "Config":
        """Get or create config instance."""
        if cls._instance is None:
            return cls.load()
        return cls._instance

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot notation.

        Args:
            key: Configuration key (e.g., "logging.level")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self

        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot notation.

        Args:
            key: Configuration key (e.g., "logging.level")
            value: Value to set
        """
        keys = key.split(".")
        obj = self

        for k in keys[:-1]:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            elif isinstance(obj, dict):
                if k not in obj:
                    obj[k] = {}
                obj = obj[k]

        final_key = keys[-1]
        if isinstance(obj, dict):
            obj[final_key] = value
        else:
            setattr(obj, final_key, value)

    def save(self, output_path: Optional[str] = None) -> None:
        """
        Save configuration to YAML file.

        Args:
            output_path: Output file path
        """
        if output_path is None:
            if self._config_path:
                output_path = str(self._config_path)
            else:
                raise ValueError("No output path specified")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        config_dict = self.dict()
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "app": self.app.dict(),
            "logging": self.logging.dict(),
            "bluetooth": self.bluetooth.dict(),
            "attacks": self.attacks.dict(),
            "ollama": self.ollama.dict(),
            "performance": self.performance,
            "tools": self.tools,
            "privileges": self.privileges,
            "reporting": self.reporting,
            "scanning": self.scanning,
            "session": self.session,
            "ui": self.ui,
        }
