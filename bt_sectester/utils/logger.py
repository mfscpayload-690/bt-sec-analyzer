"""
Structured logging system for BT-SecTester.

Provides JSON-structured logging with rotation, audit trails, and UI integration.
"""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

import structlog


class AuditLogger:
    """Dedicated audit logger for security-sensitive operations."""

    def __init__(self, audit_file: Path):
        """
        Initialize audit logger.

        Args:
            audit_file: Path to audit log file
        """
        self.audit_file = audit_file
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)

    def log_action(
        self,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        user: str = "system",
        ethical_mode: bool = True,
    ) -> None:
        """
        Log an action to the audit trail.

        Args:
            action: Action being performed
            details: Additional action details
            user: User performing action
            ethical_mode: Whether ethical mode is enabled
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user": user,
            "ethical_mode": ethical_mode,
            "details": details or {},
        }

        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


class UILogHandler(logging.Handler):
    """Custom handler to send logs to UI in real-time."""

    def __init__(self, callback: Optional[callable] = None):
        """
        Initialize UI log handler.

        Args:
            callback: Function to call with log records (for UI updates)
        """
        super().__init__()
        self.callback = callback
        self.buffer = []
        self.max_buffer_size = 1000

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record.

        Args:
            record: Log record to emit
        """
        try:
            log_entry = self.format(record)
            self.buffer.append(log_entry)

            # Keep buffer size manageable
            if len(self.buffer) > self.max_buffer_size:
                self.buffer = self.buffer[-self.max_buffer_size :]

            # Send to UI if callback is set
            if self.callback:
                self.callback(log_entry)
        except Exception:
            self.handleError(record)

    def get_buffer(self) -> list:
        """Get current log buffer."""
        return self.buffer.copy()

    def clear_buffer(self) -> None:
        """Clear log buffer."""
        self.buffer.clear()


def setup_logger(
    name: str = "bt_sectester",
    level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[Path] = None,
    console: bool = True,
    ui_callback: Optional[callable] = None,
) -> structlog.BoundLogger:
    """
    Setup structured logger with multiple outputs.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format (json or text)
        log_file: Path to log file
        console: Enable console output
        ui_callback: Callback for UI log updates

    Returns:
        Configured structured logger
    """
    # Convert level string to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[],
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Remove default handlers

    # Setup handlers
    handlers = []

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        handlers.append(console_handler)

    # File handler with rotation
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(log_level)
        handlers.append(file_handler)

    # UI handler
    if ui_callback:
        ui_handler = UILogHandler(callback=ui_callback)
        ui_handler.setLevel(log_level)
        handlers.append(ui_handler)

    # Add handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)

    # Configure structlog processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add JSON or console renderer based on format
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Get and return logger
    logger = structlog.get_logger(name)
    return logger


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to calling module)

    Returns:
        Logger instance
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
