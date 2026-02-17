#!/bin/bash
# Install script for bt-sec-analyzer on Arch Linux

set -e

echo "Installing bt-sec-analyzer on Arch Linux..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root."
    exit 1
fi

# Update system
echo "[*] Updating system..."
sudo pacman -Syu --noconfirm

# Install system dependencies
echo "[*] Installing system dependencies..."
sudo pacman -S --needed --noconfirm \
    python \
    python-pip \
    bluez \
    bluez-utils \
    git \
    base-devel

# Optional dependencies
echo "[*] Installing optional dependencies..."
sudo pacman -S --needed --noconfirm \
    wireshark-cli \
    bettercap \
    || echo "Some optional dependencies failed to install"

# Install Poetry
if ! command -v poetry &> /dev/null; then
    echo "[*] Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install Python dependencies
echo "[*] Installing Python dependencies..."
poetry install

# Enable Bluetooth service
echo "[*] Enabling Bluetooth service..."
sudo systemctl enable bluetooth.service
sudo systemctl start bluetooth.service

# Add user to bluetooth group
echo "[*] Adding user to bluetooth group..."
sudo usermod -aG bluetooth "$USER"

# Create directories
echo "[*] Creating directories..."
mkdir -p logs reports sessions captures

# Install Ollama (optional)
read -p "Install Ollama for AI features? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[*] Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh

    echo "[*] Pulling Qwen Coder model..."
    ollama pull qwen2.5-coder:7b
fi

echo ""
echo "[+] Installation complete!"
echo ""
echo "IMPORTANT: You need to log out and back in for group changes to take effect."
echo ""
echo "After logging back in, run:"
echo "  poetry run python scripts/setup.py  # Verify installation"
echo "  poetry run bt-sec-analyzer-cli --help   # Use CLI"
echo ""
