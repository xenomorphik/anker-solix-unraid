#!/bin/bash
set -e

VERSION="${1:-2026.08.28}"
DIST_DIR="dist"
BUILD_DIR="build_tmp"

echo "Building Anker Solix Unraid Plugin v${VERSION}..."

rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR/usr/local/emhttp/plugins/anker-solix" "$DIST_DIR"

# Copy plugin files
cp -r usr/local/emhttp/plugins/anker-solix/* "$BUILD_DIR/usr/local/emhttp/plugins/anker-solix/"

# Create proper xz-compressed txz package archive
python3 -c "import tarfile; tar = tarfile.open('${DIST_DIR}/anker-solix-${VERSION}.txz', 'w:xz'); tar.add('${BUILD_DIR}/usr', arcname='usr'); tar.close()"
rm -rf "$BUILD_DIR"

echo "Package successfully built at: ${DIST_DIR}/anker-solix-${VERSION}.txz"
