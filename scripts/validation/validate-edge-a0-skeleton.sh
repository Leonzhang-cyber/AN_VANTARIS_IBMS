#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EDGE_DIR="${ROOT_DIR}/AN_VANTARIS_EDGE"

required_files=(
  "${EDGE_DIR}/package.json"
  "${EDGE_DIR}/tsconfig.json"
  "${EDGE_DIR}/README.md"
  "${EDGE_DIR}/runtime-data/.gitkeep"
)

required_dirs=(
  "${EDGE_DIR}/src/runtime"
  "${EDGE_DIR}/src/connectors"
  "${EDGE_DIR}/src/protocol-plugins"
  "${EDGE_DIR}/src/mapping"
  "${EDGE_DIR}/src/normalization"
  "${EDGE_DIR}/src/buffer"
  "${EDGE_DIR}/src/health"
  "${EDGE_DIR}/src/diagnostics"
  "${EDGE_DIR}/src/security"
  "${EDGE_DIR}/src/dry-run"
  "${EDGE_DIR}/docs"
  "${EDGE_DIR}/examples"
)

if [[ ! -d "${EDGE_DIR}" ]]; then
  echo "FAIL: AN_VANTARIS_EDGE directory not found"
  exit 1
fi

for file in "${required_files[@]}"; do
  [[ -f "${file}" ]] || { echo "FAIL: missing file ${file}"; exit 1; }
done

for dir in "${required_dirs[@]}"; do
  [[ -d "${dir}" ]] || { echo "FAIL: missing directory ${dir}"; exit 1; }
done

if find "${EDGE_DIR}" -type f | rg -n "base_driver\.py|http_driver\.py|isapi_driver\.py|isup_driver\.py|modbus_driver\.py|mqtt_driver\.py|rtsp_driver\.py|dao\.py|models\.py|device_manager\.py|sse_api" >/dev/null; then
  echo "FAIL: legacy driver/runtime source detected in AN_VANTARIS_EDGE"
  exit 1
fi

if find "${EDGE_DIR}" -type f | rg -n "\.env$|\.env\." >/dev/null; then
  echo "FAIL: .env file detected in AN_VANTARIS_EDGE"
  exit 1
fi

if rg -n "src/Iot/dao|src/Iot/models|src/api/iot|sse_api|DeviceDAO|FieldMappingDAO|MethodMappingDAO|db\.session|sqlalchemy" "${EDGE_DIR}/src" >/dev/null; then
  echo "FAIL: forbidden DAO/SSE/API coupling string detected"
  exit 1
fi

for json_file in "${EDGE_DIR}/examples/"*.json; do
  python3 -m json.tool "${json_file}" >/dev/null
done

echo "PASS: EDGE A0 skeleton validation passed"
