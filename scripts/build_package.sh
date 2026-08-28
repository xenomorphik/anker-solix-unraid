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

# Create txz package archive
cd "$BUILD_DIR"
tar -cf "../${DIST_DIR}/anker-solix-${VERSION}.tar" usr/
cd ..
gzip -c "${DIST_DIR}/anker-solix-${VERSION}.tar" > "${DIST_DIR}/anker-solix-${VERSION}.txz"
rm -f "${DIST_DIR}/anker-solix-${VERSION}.tar"
rm -rf "$BUILD_DIR"

echo "Package successfully built at: ${DIST_DIR}/anker-solix-${VERSION}.txz"
