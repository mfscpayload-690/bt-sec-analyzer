#!/bin/bash
# Build standalone executable using PyInstaller

set -e

echo "Building bt-sec-analyzer standalone executable..."

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Please install Poetry first."
    exit 1
fi

# Activate virtual environment
echo "[*] Setting up environment..."
poetry install

# Install PyInstaller if not present
poetry add --group dev pyinstaller

# Create build directory
mkdir -p build dist

# Build executable
echo "[*] Building executable with PyInstaller..."
poetry run pyinstaller \
    --name bt-sec-analyzer \
    --onefile \
    --hidden-import=bt_sectester \
    --hidden-import=bluetooth \
    --hidden-import=bleak \
    --hidden-import=structlog \
    --hidden-import=reportlab \
    --hidden-import=ollama \
    --add-data "configs:configs" \
    --collect-all bt_sectester \
    --noconfirm \
    bt_sectester/__main__.py

echo "[+] Build complete!"
echo "[+] Executable location: dist/bt-sec-analyzer"
echo ""
echo "Run with:"
echo "  ./dist/bt-sec-analyzer"
