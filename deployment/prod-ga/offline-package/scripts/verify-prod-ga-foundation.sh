#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
MANIFEST_PATH="$ROOT_DIR/deployment/prod-ga/offline-package/manifest/prod-ga-foundation-package-manifest.v1.json"
PACKAGES=(
  "AN_VANTARIS_ONE/packages/AN_VANTARIS_EDGE"
  "AN_VANTARIS_ONE/packages/AN_VANTARIS_LINK"
  "AN_VANTARIS_ONE/packages/AN_VANTARIS_DB"
  "AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts"
)

echo "[ONE-PROD-GA-R4] Production GA foundation package verification"
echo "manifest=$MANIFEST_PATH"

if [[ ! -f "$MANIFEST_PATH" ]]; then
  echo "FAIL: manifest missing"
  exit 1
fi

for package_path in "${PACKAGES[@]}"; do
  absolute_path="$ROOT_DIR/$package_path"
  if [[ ! -d "$absolute_path" ]]; then
    echo "FAIL: package directory missing: $package_path"
    exit 1
  fi
  file_count="$(find "$absolute_path" -type f | wc -l | tr -d ' ')"
  if [[ "$file_count" == "0" ]]; then
    echo "FAIL: package has zero files: $package_path"
    exit 1
  fi
  echo "PASS: $package_path fileCount=$file_count"
done

for package_path in "${PACKAGES[@]}"; do
  absolute_path="$ROOT_DIR/$package_path"
  forbidden="$(
    find "$absolute_path" \( \
      -name ".env" -o \
      -name ".env.*" -o \
      -name "*.pem" -o \
      -name "*.key" -o \
      -name "*.p12" -o \
      -name "*.crt" -o \
      -name "node_modules" -o \
      -name "dist" -o \
      -name "build" -o \
      -name ".runtime" -o \
      -name "__pycache__" \
    \) -print
  )"
  if [[ -n "$forbidden" ]]; then
    echo "FAIL: forbidden files found under $package_path"
    echo "$forbidden"
    exit 1
  fi
done

echo "PASS: forbidden file scan is empty"
echo "PASS: verification completed read-only"

