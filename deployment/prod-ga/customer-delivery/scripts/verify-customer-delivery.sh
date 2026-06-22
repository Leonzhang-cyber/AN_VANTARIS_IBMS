#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
PACKAGES_DIR="${ROOT_DIR}/AN_VANTARIS_ONE/packages"
MANIFEST="${ROOT_DIR}/deployment/prod-ga/customer-delivery/customer-delivery.manifest.v1.json"

count_files() {
  local package_name="$1"
  find "${PACKAGES_DIR}/${package_name}" -type f | wc -l | tr -d ' '
}

echo "VANTARIS ONE Customer Delivery verify"
echo "No install, rollback, DB migration, service start, or runtime activation is performed."

test -f "${MANIFEST}"
test -f "${ROOT_DIR}/deployment/prod-ga/customer-delivery/ui/ENGINEER_INSTALLER_CONSOLE_SPEC.md"
test -f "${ROOT_DIR}/deployment/prod-ga/customer-delivery/ui/CUSTOMER_DELIVERY_UI_FLOW.md"
test -f "${ROOT_DIR}/deployment/prod-ga/customer-delivery/checklists/CUSTOMER_GA_ACTIVATION_CHECKLIST.md"
test -f "${ROOT_DIR}/deployment/prod-ga/customer-delivery/checklists/OFFLINE_DEPLOYMENT_ACCEPTANCE_CHECKLIST.md"

[[ "$(count_files AN_VANTARIS_EDGE)" == "248" ]]
[[ "$(count_files AN_VANTARIS_LINK)" == "153" ]]
[[ "$(count_files AN_VANTARIS_DB)" == "14" ]]
[[ "$(count_files AN_VANTARIS_Contracts)" == "174" ]]

for marker in \
  ONE_PROD_GA_R8_FINAL_EXPORT_PACKAGE_BUILDER_PASS \
  ONE_PROD_GA_R7_FINAL_FOUNDATION_PACKAGE_CONSOLIDATED_RELEASE_INDEX_PASS \
  ONE_PROD_GA_R6_FULL_EDGE_RUNTIME_RESYNC_GATE_PASS; do
  if ! /usr/bin/grep -R "${marker}" "${ROOT_DIR}" --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv >/dev/null; then
    echo "Missing marker: ${marker}"
    exit 1
  fi
done

forbidden="$(find "${PACKAGES_DIR}" "${ROOT_DIR}/deployment/prod-ga/customer-delivery" \( -name ".env" -o -name ".env.*" -o -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "*.crt" -o -name "node_modules" -o -name "dist" -o -name "build" -o -name ".runtime" -o -name "__pycache__" -o -name "._*" \) -print)"
if [[ -n "${forbidden}" ]]; then
  echo "${forbidden}"
  exit 1
fi

echo "VERIFY_CUSTOMER_DELIVERY_PASS"
