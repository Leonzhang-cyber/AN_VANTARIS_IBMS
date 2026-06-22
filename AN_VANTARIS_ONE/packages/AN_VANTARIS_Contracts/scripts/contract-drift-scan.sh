#!/usr/bin/env bash
# UFMS-VAL-0: Contracts authority must not drift into consumer-generated copies.
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
  echo "contract-drift-scan: FAIL (could not locate repo root)" >&2
  exit 1
}

ROOT="$(find_repo_root "$(cd "$(dirname "$0")" && pwd)")"
cd "$ROOT"

BANNER="AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT."
BANNER_REGEX='AUTO-GENERATED FROM AN_VANTARIS_Contracts\. DO NOT EDIT\.'
FAIL=0
WARN=0

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "contract-drift-scan: FAIL (missing required file: $path)"
    FAIL=1
  fi
}

require_dir() {
  local path="$1"
  if [[ ! -d "$path" ]]; then
    echo "contract-drift-scan: FAIL (missing required directory: $path)"
    FAIL=1
  fi
}

P0_AUTHORITY_FILES=(
  AN_VANTARIS_Contracts/schemas/wire-event-v1.schema.json
  AN_VANTARIS_Contracts/schemas/machine-identity-ref-v1.schema.json
  AN_VANTARIS_Contracts/schemas/signature-headers-v1.schema.json
  AN_VANTARIS_Contracts/schemas/signed-handoff-envelope-v1.schema.json
  AN_VANTARIS_Contracts/schemas/edge-handoff-event-v1.schema.json
  AN_VANTARIS_Contracts/schemas/delivery-ack.v1.schema.json
  AN_VANTARIS_Contracts/openapi/edge-to-link-handoff.openapi.yaml
  AN_VANTARIS_Contracts/dto-examples/wire-event.example.json
  AN_VANTARIS_Contracts/dto-examples/machine-identity-ref.example.json
  AN_VANTARIS_Contracts/dto-examples/signature-headers.example.json
  AN_VANTARIS_Contracts/dto-examples/signed-handoff-envelope.example.json
  AN_VANTARIS_Contracts/dto-examples/edge-handoff-event.example.json
  AN_VANTARIS_Contracts/dto-examples/delivery-ack-partial-success.example.json
  AN_VANTARIS_Contracts/dto-examples/delivery-ack-retryable-failure.example.json
  AN_VANTARIS_Contracts/engineering-handoff/ENGINEER_README.md
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_ENGINEER_QUICKSTART_V1.md
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_HANDOFF_PACK_INDEX_V1.md
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_FIELD_MAPPING_V1.md
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_INTEGRATION_TEST_CHECKLIST_V1.md
  AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_REQUEST_EXAMPLES_V1.md
  AN_VANTARIS_Contracts/engineering-handoff/DB_ENGINEER_CONTRACT_NOTE_V1.md
)

AUTHORITY_DIRS=(
  AN_VANTARIS_Contracts/schemas
  AN_VANTARIS_Contracts/openapi
  AN_VANTARIS_Contracts/status
  AN_VANTARIS_Contracts/errors
  AN_VANTARIS_Contracts/dto-examples
  AN_VANTARIS_Contracts/versions
  AN_VANTARIS_Contracts/engineering-handoff
)

GENERATED_DIRS_REQUIRED=(
  AN_VANTARIS_EDGE/src/generated/contracts
  AN_VANTARIS_EDGE/src/generated/protocol
  AN_VANTARIS_EDGE/src/generated/security
  AN_VANTARIS_LINK/src/generated/contracts
  AN_VANTARIS_LINK/src/generated/protocol
  AN_VANTARIS_LINK/src/generated/security
)

for dir in "${AUTHORITY_DIRS[@]}"; do
  require_dir "$dir"
done

for dir in "${GENERATED_DIRS_REQUIRED[@]}"; do
  require_dir "$dir"
done

for f in "${P0_AUTHORITY_FILES[@]}"; do
  require_file "$f"
done

# Authority tree must not contain generated-consumer banner text.
if rg -n -x "$BANNER_REGEX" AN_VANTARIS_Contracts --glob '!**/scripts/**' >/dev/null 2>&1; then
  echo "DRIFT: generated banner inside Contracts authority"
  rg -n -x "$BANNER_REGEX" AN_VANTARIS_Contracts --glob '!**/scripts/**' || true
  FAIL=1
fi

# Generated contracts consumers must carry generated banner in README.
for readme in \
  AN_VANTARIS_EDGE/src/generated/contracts/README.md \
  AN_VANTARIS_LINK/src/generated/contracts/README.md; do
  if [[ ! -f "$readme" ]]; then
    echo "contract-drift-scan: FAIL (missing generated contracts README: $readme)"
    FAIL=1
    continue
  fi
  if ! rg -n -x "$BANNER_REGEX" "$readme" >/dev/null 2>&1; then
    echo "DRIFT: missing generated banner: $readme"
    FAIL=1
  fi
done

# Placeholder-only generated trees are acceptable for now.
for dir in "${GENERATED_DIRS_REQUIRED[@]}"; do
  if [[ ! -f "$dir/README.md" ]]; then
    echo "WARN: generated placeholder README missing: $dir/README.md"
    WARN=1
  fi
done

# Contracts authority must not import runtime package paths.
IMPORT_PATTERN="(import[[:space:]].*from[[:space:]]*['\"][^'\"]*(AN_VANTARIS_EDGE|AN_VANTARIS_LINK|AN_VANTARIS_Code|AN_VANTARIS_DB|AN_VANTARIS_Console|AN_VANTARIS_NexusAI)[^'\"]*['\"]|require\\([[:space:]]*['\"][^'\"]*(AN_VANTARIS_EDGE|AN_VANTARIS_LINK|AN_VANTARIS_Code|AN_VANTARIS_DB|AN_VANTARIS_Console|AN_VANTARIS_NexusAI)[^'\"]*['\"][[:space:]]*\\)|import[[:space:]].*from[[:space:]]*['\"](\\.\\./AN_VANTARIS|\\.\\./\\.\\./AN_VANTARIS)[^'\"]*['\"]|require\\([[:space:]]*['\"](\\.\\./AN_VANTARIS|\\.\\./\\.\\./AN_VANTARIS)[^'\"]*['\"][[:space:]]*\\))"
if rg -n "$IMPORT_PATTERN" AN_VANTARIS_Contracts --glob '!**/scripts/**' >/dev/null 2>&1; then
  echo "DRIFT: runtime package import leakage in Contracts authority"
  rg -n "$IMPORT_PATTERN" AN_VANTARIS_Contracts --glob '!**/scripts/**' || true
  FAIL=1
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "contract-drift-scan: FAIL (warnings=$WARN)"
  exit 1
fi

echo "contract-drift-scan: PASS (warnings=$WARN)"
exit 0
