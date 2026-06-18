#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EDGE_DIR="${ROOT_DIR}/AN_VANTARIS_EDGE"

[[ -d "${EDGE_DIR}" ]] || { echo "FAIL: AN_VANTARIS_EDGE not found"; exit 1; }

cd "${EDGE_DIR}"
npm run typecheck >/dev/null
cd "${ROOT_DIR}"

bash scripts/validation/validate-edge-a0-skeleton.sh >/dev/null

[[ -f "${EDGE_DIR}/src/connectors/connector-registry.ts" ]] || {
  echo "FAIL: connector-registry.ts missing"
  exit 1
}
[[ -f "${EDGE_DIR}/src/dry-run/connector-registry-dry-run.ts" ]] || {
  echo "FAIL: connector-registry-dry-run.ts missing"
  exit 1
}

if find "${EDGE_DIR}" -type f | rg -n "base_driver\.py|http_driver\.py|isapi_driver\.py|isup_driver\.py|modbus_driver\.py|mqtt_driver\.py|rtsp_driver\.py|dao\.py|models\.py|device_manager\.py|sse_api" >/dev/null; then
  echo "FAIL: legacy driver/runtime source copied"
  exit 1
fi

if rg -n "src/Iot/dao|src/Iot/models|src/api/iot|sse_api|DeviceDAO|FieldMappingDAO|MethodMappingDAO|db\.session|sqlalchemy|flask|prisma" "${EDGE_DIR}/src" >/dev/null; then
  echo "FAIL: forbidden DAO/SSE/API coupling found"
  exit 1
fi

if find "${EDGE_DIR}" -type f | rg -n "\.env$|\.env\." >/dev/null; then
  echo "FAIL: .env file detected"
  exit 1
fi

if [[ -d "${ROOT_DIR}/AN_VANTARIS_LINK" ]]; then
  echo "FAIL: AN_VANTARIS_LINK runtime should not exist"
  exit 1
fi

echo "PASS: EDGE A1 connector registry dry-run validation passed"
