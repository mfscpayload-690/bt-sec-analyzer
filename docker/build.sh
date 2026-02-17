#!/bin/bash
# Build script for bt-sec-analyzer containers

set -e

echo "Building bt-sec-analyzer containers..."

# Build main application container
echo "[*] Building main application container..."
podman build -t bt-sec-analyzer:latest -f docker/Dockerfile .

# Build Bettercap container
echo "[*] Building Bettercap container..."
podman build -t bt-sec-analyzer-bettercap:latest -f docker/Dockerfile.bettercap docker/

echo "[+] Build complete!"
echo ""
echo "Run with:"
echo "  podman run -it --privileged --network=host bt-sec-analyzer:latest"
echo ""
echo "Run Bettercap with:"
echo "  podman run -it --privileged --network=host bt-sec-analyzer-bettercap:latest"
