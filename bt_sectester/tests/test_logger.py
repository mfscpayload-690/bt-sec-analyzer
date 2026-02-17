"""
Tests for logger functionality.
"""

import tempfile
from pathlib import Path

import structlog

from bt_sectester.utils.logger import AuditLogger, setup_logger


def test_setup_logger():
    """Test logger setup."""
    logger = setup_logger(
        name="test_logger",
        level="INFO",
        log_format="json",
        console=False,
    )

    assert logger is not None
    assert isinstance(logger, structlog.BoundLogger)


def test_setup_logger_with_file():
    """Test logger setup with file output."""
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
        log_file = Path(f.name)

    try:
        logger = setup_logger(
            name="test_logger",
            level="DEBUG",
            log_format="json",
            log_file=log_file,
            console=False,
        )

        logger.info("test message", key="value")

        # Check file exists and has content
        assert log_file.exists()
        content = log_file.read_text()
        assert "test message" in content
        assert "key" in content

    finally:
        if log_file.exists():
            log_file.unlink()


def test_audit_logger():
    """Test audit logger."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        audit_file = Path(f.name)

    try:
        audit_logger = AuditLogger(audit_file)

        audit_logger.log_action(
            action="test_action",
            details={"key": "value"},
            user="test_user",
            ethical_mode=True,
        )

        # Check audit file
        assert audit_file.exists()
        content = audit_file.read_text()
        assert "test_action" in content
        assert "test_user" in content

    finally:
        if audit_file.exists():
            audit_file.unlink()
