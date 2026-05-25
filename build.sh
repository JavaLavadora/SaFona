#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VERSION=$(python3 -c "
import re
text = open('pyproject.toml').read()
m = re.search(r'version\s*=\s*\"([^\"]+)\"', text)
print(m.group(1) if m else '0.0.0')
")

TARGET="${1:-linux}"

echo "=== Sa Fona build (v${VERSION}, target: ${TARGET}) ==="

# Clean previous build artifacts.
rm -rf build/ dist/

# Ensure PyInstaller is available.
if ! python3 -m PyInstaller --version &>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

echo "Running PyInstaller..."
python3 -m PyInstaller safona.spec --noconfirm

if [ ! -d "dist/SaFona" ]; then
    echo "ERROR: PyInstaller output not found at dist/SaFona/"
    exit 1
fi

# Generate player-facing README from template.
if [ -f "dist_assets/README.txt.template" ]; then
    sed "s/{{VERSION}}/${VERSION}/g" dist_assets/README.txt.template \
        > dist/SaFona/README.txt
    echo "Generated README.txt (v${VERSION})"
fi

# Create zip archive.
PLATFORM_SUFFIX="${TARGET}"
ZIP_NAME="SaFona-${PLATFORM_SUFFIX}.zip"
cd dist
zip -r "${ZIP_NAME}" SaFona/
cd ..

FINAL_SIZE=$(du -sh "dist/${ZIP_NAME}" | cut -f1)
echo ""
echo "=== Build complete ==="
echo "  Output: dist/${ZIP_NAME} (${FINAL_SIZE})"
echo ""
echo "To upload with butler:"
echo "  butler push dist/${ZIP_NAME} <username>/sa-fona:${PLATFORM_SUFFIX}"
