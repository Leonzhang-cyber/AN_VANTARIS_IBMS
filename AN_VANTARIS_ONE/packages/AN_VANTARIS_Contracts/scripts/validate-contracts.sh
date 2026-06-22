#!/usr/bin/env bash
set -euo pipefail

find_repo_root() {
  local dir="$1"
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/VANTARIS_UFMS_PACKAGE_COORDINATION.md" ]]; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  echo "validate-contracts: FAIL (could not locate repo root)" >&2
  exit 1
}

ROOT="$(find_repo_root "$(cd "$(dirname "$0")" && pwd)")"
cd "$ROOT"

FAIL=0
WARN=0

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "FAIL: missing required file: $path"
    FAIL=1
  fi
}

require_dir() {
  local path="$1"
  if [[ ! -d "$path" ]]; then
    echo "FAIL: missing required directory: $path"
    FAIL=1
  fi
}

require_nonempty_file() {
  local path="$1"
  if [[ ! -s "$path" ]]; then
    echo "FAIL: required non-empty file missing or empty: $path"
    FAIL=1
  fi
}

require_contains() {
  local path="$1"
  local needle="$2"
  if [[ -f "$path" ]]; then
    if ! rg -n -F "$needle" "$path" >/dev/null 2>&1; then
      echo "FAIL: expected content not found in $path: $needle"
      FAIL=1
    fi
  fi
}

echo "validate-contracts: checking authority files"
for f in \
  AN_VANTARIS_Contracts/README.md \
  AN_VANTARIS_Contracts/VERSION \
  AN_VANTARIS_Contracts/GOVERNANCE.md \
  AN_VANTARIS_Contracts/contract-manifest.json \
  AN_VANTARIS_Contracts/CHANGELOG.md; do
  require_file "$f"
done

echo "validate-contracts: checking required directories"
for d in \
  AN_VANTARIS_Contracts/schemas \
  AN_VANTARIS_Contracts/openapi \
  AN_VANTARIS_Contracts/dto-examples \
  AN_VANTARIS_Contracts/versions \
  AN_VANTARIS_Contracts/standards \
  AN_VANTARIS_Contracts/canonical \
  AN_VANTARIS_Contracts/db \
  AN_VANTARIS_Contracts/security \
  AN_VANTARIS_Contracts/engineering-handoff; do
  require_dir "$d"
done

echo "validate-contracts: checking P0 schema files"
for f in \
  AN_VANTARIS_Contracts/schemas/wire-event-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/machine-identity-ref-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/signature-headers-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/signed-handoff-envelope-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/edge-handoff-event-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/delivery-ack.v1.schema.json; do
  require_file "$f"
done

echo "validate-contracts: checking P1 common schema files"
for f in \
  AN_VANTARIS_Contracts/schemas/common-identifiers-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/common-trace-context-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/common-audit-fields-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/common-health-status-v1.schema.json; do
  require_file "$f"
done

echo "validate-contracts: checking P1 canonical schema files"
for f in \
  AN_VANTARIS_Contracts/schemas/tenant-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/site-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/building-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/floor-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/space-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/gateway-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/connector-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/source-system-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/asset-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/device-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/point-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/telemetry-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/event-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/alarm-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/evidence-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/health-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/throughput-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/sync-batch-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/audit-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/config-version-v1.schema.json; do
  require_file "$f"
done

echo "validate-contracts: checking P1C reliability schema files"
for f in \
  AN_VANTARIS_Contracts/schemas/link-delivery-attempt-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/link-retry-policy-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/link-dlq-item-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/link-replay-request-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/link-replay-result-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/link-delivery-batch-v1.schema.json \
  AN_VANTARIS_Contracts/schemas/link-partition-state-v1.schema.json; do
  require_file "$f"
done

echo "validate-contracts: checking P0 OpenAPI"
require_file AN_VANTARIS_Contracts/openapi/edge-to-link-handoff.openapi.yaml

echo "validate-contracts: checking P0 examples"
for f in \
  AN_VANTARIS_Contracts/dto-examples/wire-event.example.json \
  AN_VANTARIS_Contracts/dto-examples/machine-identity-ref.example.json \
  AN_VANTARIS_Contracts/dto-examples/signature-headers.example.json \
  AN_VANTARIS_Contracts/dto-examples/signed-handoff-envelope.example.json \
  AN_VANTARIS_Contracts/dto-examples/edge-handoff-event.example.json \
  AN_VANTARIS_Contracts/dto-examples/delivery-ack-partial-success.example.json \
  AN_VANTARIS_Contracts/dto-examples/delivery-ack-retryable-failure.example.json; do
  require_file "$f"
done

echo "validate-contracts: checking P1 canonical examples"
for f in \
  AN_VANTARIS_Contracts/dto-examples/canonical/tenant.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/site.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/building.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/floor.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/space.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/gateway.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/connector.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/source-system.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/asset.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/device.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/point.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/telemetry.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/event.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/alarm.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/evidence.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/health.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/throughput.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/sync-batch.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/audit.example.json \
  AN_VANTARIS_Contracts/dto-examples/canonical/config-version.example.json; do
  require_file "$f"
done

echo "validate-contracts: checking P1C reliability examples"
for f in \
  AN_VANTARIS_Contracts/dto-examples/reliability/link-delivery-attempt.example.json \
  AN_VANTARIS_Contracts/dto-examples/reliability/link-retry-policy.example.json \
  AN_VANTARIS_Contracts/dto-examples/reliability/link-dlq-item.example.json \
  AN_VANTARIS_Contracts/dto-examples/reliability/link-replay-request.example.json \
  AN_VANTARIS_Contracts/dto-examples/reliability/link-replay-result.example.json \
  AN_VANTARIS_Contracts/dto-examples/reliability/link-delivery-batch.example.json \
  AN_VANTARIS_Contracts/dto-examples/reliability/link-partition-state.example.json; do
  require_file "$f"
done

echo "validate-contracts: checking engineer handoff files"
for f in \
  AN_VANTARIS_Contracts/engineering-handoff/ENGINEER_README.md \
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_ENGINEER_QUICKSTART_V1.md \
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_HANDOFF_PACK_INDEX_V1.md \
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_FIELD_MAPPING_V1.md \
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_INTEGRATION_TEST_CHECKLIST_V1.md \
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_REQUEST_EXAMPLES_V1.md \
  AN_VANTARIS_Contracts/engineering-handoff/DB_ENGINEER_CONTRACT_NOTE_V1.md \
  AN_VANTARIS_Contracts/engineering-handoff/LINK_RELIABILITY_ENGINEER_GUIDE_V1.md; do
  require_file "$f"
done

echo "validate-contracts: checking P1C reliability docs/OpenAPI"
for f in \
  AN_VANTARIS_Contracts/versions/link-reliability-profile-v1.md \
  AN_VANTARIS_Contracts/openapi/link-reliability.openapi.yaml; do
  require_file "$f"
done

echo "validate-contracts: checking P2A0 security baseline files"
for f in \
  AN_VANTARIS_Contracts/security/iec62443-security-baseline.v1.md \
  AN_VANTARIS_Contracts/security/auditability-contract.v1.md \
  AN_VANTARIS_Contracts/security/industrial-safety-cyber-boundary.v1.md \
  AN_VANTARIS_Contracts/security/security-traceability-matrix.v1.md \
  AN_VANTARIS_Contracts/security/deployment-profile-security-baseline.v1.md; do
  require_file "$f"
done

echo "validate-contracts: checking P1B DB mapping files"
for f in \
  AN_VANTARIS_Contracts/db/canonical-to-db-map.v1.yaml \
  AN_VANTARIS_Contracts/db/field-type-mapping.v1.yaml \
  AN_VANTARIS_Contracts/db/migration-metadata-contract.v1.yaml \
  AN_VANTARIS_Contracts/db/DB_MAPPING_README_V1.md; do
  require_file "$f"
  require_nonempty_file "$f"
done

echo "validate-contracts: checking P1B DB mapping content markers"
require_contains AN_VANTARIS_Contracts/db/canonical-to-db-map.v1.yaml "schemaVersion"
require_contains AN_VANTARIS_Contracts/db/canonical-to-db-map.v1.yaml "contractVersion"
require_contains AN_VANTARIS_Contracts/db/canonical-to-db-map.v1.yaml "canonicalObjectMappings"
require_contains AN_VANTARIS_Contracts/db/canonical-to-db-map.v1.yaml "EDGE/LINK must not direct-write UFMS DB"

require_contains AN_VANTARIS_Contracts/db/field-type-mapping.v1.yaml "schemaVersion"
require_contains AN_VANTARIS_Contracts/db/field-type-mapping.v1.yaml "contractVersion"

require_contains AN_VANTARIS_Contracts/db/migration-metadata-contract.v1.yaml "schemaVersion"
require_contains AN_VANTARIS_Contracts/db/migration-metadata-contract.v1.yaml "contractVersion"

echo "validate-contracts: parsing all JSON files"
python3 - <<'PY'
import json
import pathlib
import sys

ok = True
for p in pathlib.Path("AN_VANTARIS_Contracts").rglob("*.json"):
    try:
        json.loads(p.read_text())
    except Exception as e:
        print(f"FAIL: JSON parse error: {p}: {e}")
        ok = False
if not ok:
    sys.exit(1)
print("JSON parse check: PASS")
PY

echo "validate-contracts: running lightweight semantic schema/example checks"
python3 AN_VANTARIS_Contracts/scripts/validate-schema-examples.py

echo "validate-contracts: checking fake secret policy in dto-examples"
SECRET_PATTERN='BEGIN PRIVATE KEY|AWS_SECRET|PASSWORD=|SECRET=|TOKEN=|real-signature|private_key|client_secret'
if rg -n -i "$SECRET_PATTERN" AN_VANTARIS_Contracts/dto-examples >/dev/null 2>&1; then
  echo "FAIL: dto-examples contain potential real secret material"
  rg -n -i "$SECRET_PATTERN" AN_VANTARIS_Contracts/dto-examples || true
  FAIL=1
fi

echo "validate-contracts: checking runtime import leakage"
IMPORT_PATTERN="(import[[:space:]].*from[[:space:]]*['\"][^'\"]*(AN_VANTARIS_EDGE|AN_VANTARIS_LINK|AN_VANTARIS_Code|AN_VANTARIS_DB|AN_VANTARIS_Console|AN_VANTARIS_NexusAI)[^'\"]*['\"]|require\\([[:space:]]*['\"][^'\"]*(AN_VANTARIS_EDGE|AN_VANTARIS_LINK|AN_VANTARIS_Code|AN_VANTARIS_DB|AN_VANTARIS_Console|AN_VANTARIS_NexusAI)[^'\"]*['\"][[:space:]]*\\)|import[[:space:]].*from[[:space:]]*['\"](\\.\\./AN_VANTARIS|\\.\\./\\.\\./AN_VANTARIS)[^'\"]*['\"]|require\\([[:space:]]*['\"](\\.\\./AN_VANTARIS|\\.\\./\\.\\./AN_VANTARIS)[^'\"]*['\"][[:space:]]*\\))"
if rg -n "$IMPORT_PATTERN" AN_VANTARIS_Contracts --glob '!**/scripts/**' >/dev/null 2>&1; then
  echo "FAIL: runtime package path leakage detected in Contracts authority"
  rg -n "$IMPORT_PATTERN" AN_VANTARIS_Contracts --glob '!**/scripts/**' || true
  FAIL=1
fi

echo "validate-contracts: checking product naming hard-block terms"
X1='AN_VANTARIS_'
X2='IB'"MS"
X3='/Users/mac/Desktop/'
X4='ibms'
X5='DEV-JWT-'"SMOKE"
X6='IB'"MS-DB-SMOKE"
X7='IB'"MS-REPO-BASELINE"
X8='IB'"MS-FE-BUILD"
HARD_BLOCK_PATTERN="${X1}${X2}|${X3}${X1}${X2}|${X4}_backend|${X4}_front|${X5}|${X6}|${X7}|${X8}"
if rg -n -i "$HARD_BLOCK_PATTERN" AN_VANTARIS_Contracts \
  --glob '!**/scripts/**' \
  --glob '!**/validation/contract-validation-baseline-v1.md' >/dev/null 2>&1; then
  echo "FAIL: forbidden cross-workspace naming markers detected in Contracts authority"
  rg -n -i "$HARD_BLOCK_PATTERN" AN_VANTARIS_Contracts \
    --glob '!**/scripts/**' \
    --glob '!**/validation/contract-validation-baseline-v1.md' || true
  FAIL=1
fi

echo "validate-contracts: checking plain future-profile terms outside allowlist (warning only)"
TERM_A='IB'"MS"
TERM_B='UI'"BMS"
PLAIN_FUTURE_PROFILE_PATTERN="\\b${TERM_A}\\b|\\b${TERM_B}\\b"
if rg -n -i "$PLAIN_FUTURE_PROFILE_PATTERN" AN_VANTARIS_Contracts \
  --glob '!**/canonical/module-profile-map.v1.md' \
  --glob '!**/contract-manifest.json' \
  --glob '!**/validation/contract-validation-baseline-v1.md' \
  --glob '!**/scripts/**' >/dev/null 2>&1; then
  echo "WARN: plain future-profile terms found outside naming allowlist files"
  rg -n -i "$PLAIN_FUTURE_PROFILE_PATTERN" AN_VANTARIS_Contracts \
    --glob '!**/canonical/module-profile-map.v1.md' \
    --glob '!**/contract-manifest.json' \
    --glob '!**/validation/contract-validation-baseline-v1.md' \
    --glob '!**/scripts/**' || true
  WARN=1
fi

echo "validate-contracts: checking DB implementation leakage (warning only)"
DB_PATTERN='@@|@id\b|@default\b|\bprisma\b|\brelation\b'
if rg -n -i "$DB_PATTERN" AN_VANTARIS_Contracts/schemas >/dev/null 2>&1; then
  echo "WARN: potential DB implementation terms found in schemas"
  rg -n -i "$DB_PATTERN" AN_VANTARIS_Contracts/schemas || true
  WARN=1
fi

echo "validate-contracts: checking certification wording guard"
CW1='IEC 62443 '"certified"
CW2='formally '"certified"
CW3='guaranteed '"certified"
CERT_GUARD_PATTERN="${CW1}|${CW2}|${CW3}"
if rg -n -i "$CERT_GUARD_PATTERN" AN_VANTARIS_Contracts >/dev/null 2>&1; then
  echo "FAIL: prohibited certification claim wording detected in Contracts authority"
  rg -n -i "$CERT_GUARD_PATTERN" AN_VANTARIS_Contracts --glob '!**/scripts/**' || true
  FAIL=1
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "validate-contracts: FAIL (warnings=$WARN)"
  exit 1
fi

echo "validate-contracts: PASS (warnings=$WARN)"
exit 0
