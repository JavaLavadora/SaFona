#!/usr/bin/env bash
# Sa Fona — Display environment setup
# Run this after a JupyterLab VM reset to reinstall display services.
# Usage: ./setup_display.sh
#
# What it installs (via apt):
#   - xvfb      : Virtual framebuffer X server (pygame needs an X display)
#   - x11vnc    : VNC server that exposes the virtual display
#   - novnc     : Browser-based VNC client served on port 6080
#
# The safona conda env (pygame, websockify, etc.) persists in
# ~/my-conda-envs/ and does NOT need reinstalling.

set -e

echo "=== Sa Fona — Display Setup ==="

# ── Check sudo ──────────────────────────────────────────────────
if ! sudo -n true 2>/dev/null; then
    echo "Error: sudo access required to install system packages."
    exit 1
fi

# ── Install system packages ─────────────────────────────────────
PACKAGES=(xvfb x11vnc novnc)
MISSING=()

for pkg in "${PACKAGES[@]}"; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        MISSING+=("$pkg")
    fi
done

if [[ ${#MISSING[@]} -eq 0 ]]; then
    echo "All display packages already installed."
else
    echo "Installing: ${MISSING[*]}"
    sudo apt-get update -qq
    sudo apt-get install -y -qq "${MISSING[@]}"
    echo "Installed: ${MISSING[*]}"
fi

# ── Verify ──────────────────────────────────────────────────────
OK=true
for cmd in Xvfb x11vnc; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "  ✓ $cmd"
    else
        echo "  ✗ $cmd NOT FOUND"
        OK=false
    fi
done

if [[ -d /usr/share/novnc ]]; then
    echo "  ✓ novnc"
else
    echo "  ✗ /usr/share/novnc NOT FOUND"
    OK=false
fi

if [[ "$OK" = true ]]; then
    echo ""
    echo "Setup complete. You can now run:"
    echo "  ./run.sh --level world1/level_1_2"
else
    echo ""
    echo "Some packages failed to install. Check the output above."
    exit 1
fi
