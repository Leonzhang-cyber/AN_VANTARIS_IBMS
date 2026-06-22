#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
PACKAGES_DIR="${ROOT_DIR}/AN_VANTARIS_ONE/packages"
R8_TARBALL="/Users/leon/Desktop/VANTARIS_FINAL_EXPORT/VANTARIS_ONE_PROD_GA_FOUNDATION_PACKAGES_R7_20260622.tar.gz"
R8_SHA_FILE="${R8_TARBALL}.sha256"

echo "VANTARIS ONE Customer Delivery precheck"
echo "Mode: DRY_RUN_ONLY"
echo "Repository: ${ROOT_DIR}"
echo "No root privileges, service starts, installs, DB migrations, or runtime activation are performed."

echo "Current directory:"
pwd

echo "OS information:"
uname -a

echo "Disk space:"
df -h "${ROOT_DIR}"

echo "Package counts:"
"${ROOT_DIR}/deployment/prod-ga/customer-delivery/scripts/package-counts-customer-delivery.sh"

echo "Required package folder check:"
for package_name in AN_VANTARIS_EDGE AN_VANTARIS_LINK AN_VANTARIS_DB AN_VANTARIS_Contracts; do
  test -d "${PACKAGES_DIR}/${package_name}"
  echo "FOUND ${package_name}"
done

echo "Forbidden file scan:"
forbidden="$(find "${PACKAGES_DIR}" "${ROOT_DIR}/deployment/prod-ga/customer-delivery" \( -name ".env" -o -name ".env.*" -o -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "*.crt" -o -name "node_modules" -o -name "dist" -o -name "build" -o -name ".runtime" -o -name "__pycache__" -o -name "._*" \) -print)"
if [[ -n "${forbidden}" ]]; then
  echo "${forbidden}"
  echo "FORBIDDEN_SCAN_FAILED"
  exit 1
fi
echo "FORBIDDEN_SCAN_EMPTY"

if [[ -f "${R8_TARBALL}" && -f "${R8_SHA_FILE}" ]]; then
  echo "R8 export tarball and checksum found."
  if command -v shasum >/dev/null 2>&1; then
    (cd "$(dirname "${R8_TARBALL}")" && shasum -a 256 -c "$(basename "${R8_SHA_FILE}")")
  else
    echo "shasum not available; checksum verification skipped by precheck."
  fi
else
  echo "R8 export tarball/checksum not present at local path; offline import can supply them later."
fi

echo "PRECHECK_CUSTOMER_DELIVERY_DRY_RUN_PASS"
