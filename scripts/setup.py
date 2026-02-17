#!/usr/bin/env python3
"""
Setup script for bt-sec-analyzer.

Checks dependencies, sets up environment, and configures system.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


class Colors:
    """Terminal colors."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(msg: str) -> None:
    """Print header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(msg: str) -> None:
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")


def print_warning(msg: str) -> None:
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")


def print_error(msg: str) -> None:
    """Print error message."""
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")


def check_command(cmd: str) -> bool:
    """Check if a command exists."""
    return shutil.which(cmd) is not None


def run_command(cmd: list, check: bool = True) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def check_system_dependencies() -> dict:
    """Check system dependencies."""
    print_header("Checking System Dependencies")

    deps = {
        "python3": check_command("python3"),
        "pip": check_command("pip") or check_command("pip3"),
        "git": check_command("git"),
        "hciconfig": check_command("hciconfig"),
        "bluetoothctl": check_command("bluetoothctl"),
        "l2ping": check_command("l2ping"),
    }

    optional_deps = {
        "tshark": check_command("tshark"),
        "bettercap": check_command("bettercap"),
        "btlejack": check_command("btlejack"),
        "ollama": check_command("ollama"),
    }

    # Display results
    for dep, available in deps.items():
        if available:
            print_success(f"{dep}: Available")
        else:
            print_error(f"{dep}: NOT FOUND (Required)")

    print("\nOptional dependencies:")
    for dep, available in optional_deps.items():
        if available:
            print_success(f"{dep}: Available")
        else:
            print_warning(f"{dep}: Not found (Optional)")

    # Check if all required deps are present
    all_required = all(deps.values())
    if not all_required:
        print_error("\nMissing required dependencies!")
        print("\nOn Arch Linux, install with:")
        print("  sudo pacman -S bluez bluez-utils python python-pip git")
        return {"status": False, "deps": deps}

    return {"status": True, "deps": {**deps, **optional_deps}}


def check_bluetooth_service() -> bool:
    """Check if bluetooth service is running."""
    print_header("Checking Bluetooth Service")

    if run_command(["systemctl", "is-active", "--quiet", "bluetooth"], check=False):
        print_success("Bluetooth service is running")
        return True
    else:
        print_warning("Bluetooth service is not running")
        print("Start it with: sudo systemctl start bluetooth")
        print("Enable on boot: sudo systemctl enable bluetooth")
        return False


def check_bluetooth_permissions() -> bool:
    """Check Bluetooth permissions."""
    print_header("Checking Bluetooth Permissions")

    # Check if user is in bluetooth group
    result = subprocess.run(["groups"], capture_output=True, text=True)
    groups = result.stdout.strip().split()

    if "bluetooth" in groups:
        print_success("User is in 'bluetooth' group")
        return True
    else:
        print_warning("User is NOT in 'bluetooth' group")
        print(f"Add with: sudo usermod -aG bluetooth {os.getenv('USER', 'USERNAME')}")
        print("Then log out and back in for changes to take effect.")
        return False


def setup_directories() -> None:
    """Create necessary directories."""
    print_header("Setting Up Directories")

    directories = [
        "logs",
        "reports",
        "sessions",
        "captures",
    ]

    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {directory}")
        else:
            print(f"  Directory exists: {directory}")


def check_ollama() -> bool:
    """Check Ollama installation and model."""
    print_header("Checking Ollama (AI Features)")

    if not check_command("ollama"):
        print_warning("Ollama not found")
        print("Install with: curl -fsSL https://ollama.com/install.sh | sh")
        return False

    print_success("Ollama is installed")

    # Check if model is available
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    if "qwen2.5-coder:7b" in result.stdout:
        print_success("Qwen Coder 7B model is available")
        return True
    else:
        print_warning("Qwen Coder 7B model not found")
        print("Pull with: ollama pull qwen2.5-coder:7b")
        return False


def install_python_dependencies() -> bool:
    """Install Python dependencies."""
    print_header("Installing Python Dependencies")

    # Check if poetry is available
    if check_command("poetry"):
        print_success("Poetry found, installing dependencies...")
        if run_command(["poetry", "install"]):
            print_success("Python dependencies installed")
            return True
        else:
            print_error("Failed to install dependencies with Poetry")
            return False
    else:
        print_warning("Poetry not found")
        print("Install Poetry with: pip install poetry")
        print("Then run: poetry install")
        return False


def main() -> int:
    """Main setup function."""
    print_header("bt-sec-analyzer Setup")

    print("This script will check dependencies and set up the environment.\n")

    # Check system dependencies
    dep_check = check_system_dependencies()
    if not dep_check["status"]:
        print_error("\nSetup cannot continue. Please install missing dependencies.")
        return 1

    # Check Bluetooth service
    check_bluetooth_service()

    # Check permissions
    check_bluetooth_permissions()

    # Setup directories
    setup_directories()

    # Check Ollama
    check_ollama()

    # Install Python dependencies
    install_python_dependencies()

    # Summary
    print_header("Setup Complete")
    print_success("System is ready for bt-sec-analyzer!")
    print("\nNext steps:")
    print("  1. Ensure Bluetooth service is running")
    print("  2. Add user to bluetooth group (if needed)")
    print("  3. Install optional tools (tshark, bettercap, etc.)")
    print("  4. Pull Ollama model (if using AI features)")
    print("\nRun the application with:")
    print("  poetry run python -m bt_sectester        # GUI mode")
    print("  poetry run bt-sec-analyzer-cli --help       # CLI mode")

    return 0


if __name__ == "__main__":
    sys.exit(main())
