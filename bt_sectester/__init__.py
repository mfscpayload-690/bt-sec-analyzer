"""
BT-SecTester - Bluetooth Security Testing Framework

Main package initialization.
"""

__version__ = "0.1.0"
__author__ = "BT-SecTester Team"
__license__ = "MIT"

# Import core components for easier access
from bt_sectester.core.engine import BTSecEngine
from bt_sectester.utils.config import Config
from bt_sectester.utils.logger import setup_logger

__all__ = ["BTSecEngine", "Config", "setup_logger", "__version__"]
