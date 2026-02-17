#!/bin/bash
# Build script for BT-SecTester containers

set -e

echo "Building BT-SecTester containers..."

# Build main application container
echo "[*] Building main application container..."
podman build -t bt-sectester:latest -f docker/Dockerfile .

# Build Bettercap container
echo "[*] Building Bettercap container..."
podman build -t bt-sectester-bettercap:latest -f docker/Dockerfile.bettercap docker/

echo "[+] Build complete!"
echo ""
echo "Run with:"
echo "  podman run -it --privileged --network=host bt-sectester:latest"
echo ""
echo "Run Bettercap with:"
echo "  podman run -it --privileged --network=host bt-sectester-bettercap:latest"
