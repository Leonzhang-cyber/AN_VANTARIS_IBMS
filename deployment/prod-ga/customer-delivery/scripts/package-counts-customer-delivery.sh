#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
PACKAGES_DIR="${ROOT_DIR}/AN_VANTARIS_ONE/packages"

count_files() {
  local package_name="$1"
  find "${PACKAGES_DIR}/${package_name}" -type f | wc -l | tr -d ' '
}

echo "VANTARIS ONE Production GA package counts"
echo "EDGE: $(count_files AN_VANTARIS_EDGE)"
echo "LINK: $(count_files AN_VANTARIS_LINK)"
echo "DB: $(count_files AN_VANTARIS_DB)"
echo "Contracts: $(count_files AN_VANTARIS_Contracts)"
