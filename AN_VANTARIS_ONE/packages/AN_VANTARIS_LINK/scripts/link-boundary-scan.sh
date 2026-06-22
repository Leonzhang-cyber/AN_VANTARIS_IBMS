#!/usr/bin/env bash
# UFMS-VAL-0: LINK must not import UFMS runtime packages directly.
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
  echo "link-boundary-scan: FAIL (could not locate repo root)" >&2
  exit 1
}

ROOT="$(find_repo_root "$(cd "$(dirname "$0")" && pwd)")"
cd "$ROOT"

LINK_ROOT="AN_VANTARIS_LINK"
SCAN_DIRS=(src tests docs)
FORBIDDEN_SRC=(
  AN_VANTARIS_DB
  AN_VANTARIS_Console
  AN_VANTARIS_NexusAI
  ../AN_VANTARIS_DB
  ../AN_VANTARIS_Console
  ../AN_VANTARIS_NexusAI
  prisma
  DATABASE_URL
)
CODE_IMPORT_PATTERNS=(
  "from 'AN_VANTARIS_Code"
  'from "AN_VANTARIS_Code'
  "import AN_VANTARIS_Code"
  "require('AN_VANTARIS_Code"
  'require("AN_VANTARIS_Code'
)

if [[ ! -d "$LINK_ROOT/src" ]]; then
  echo "link-boundary-scan: SKIP (AN_VANTARIS_LINK/src not present — expected on EDGE/LINK computer or not yet extracted)"
  exit 0
fi

FOUND=0
doc_allows() {
  grep -Eiq '(forbidden|do not|boundary|isolation|not allowed|stub|contract|delivery)' <<< "$1"
}

for sub in "${SCAN_DIRS[@]}"; do
  dir="$LINK_ROOT/$sub"
  [[ -d "$dir" ]] || continue
  while IFS= read -r -d '' file; do
    rel="${file#./}"
    is_doc=0
    [[ "$rel" == *"/docs/"* || "$rel" == *.md ]] && is_doc=1
    is_test=0
    [[ "$sub" == "tests" || "$rel" == *"/tests/"* ]] && is_test=1

    while IFS= read -r line || [[ -n "$line" ]]; do
      for pattern in "${FORBIDDEN_SRC[@]}"; do
        if grep -Fq -- "$pattern" <<< "$line"; then
          if [[ "$is_doc" -eq 1 ]] && doc_allows "$line"; then continue; fi
          if [[ "$is_test" -eq 1 ]] && doc_allows "$line"; then continue; fi
          echo "BOUNDARY: $rel ($pattern)"
          FOUND=1
        fi
      done
      if [[ "$sub" == "src" ]]; then
        for pattern in "${CODE_IMPORT_PATTERNS[@]}"; do
          if grep -Fq -- "$pattern" <<< "$line"; then
            echo "BOUNDARY import: $rel ($pattern)"
            FOUND=1
          fi
        done
      fi
    done < "$file"
  done < <(find "$dir" -type f \
    -not -path '*/node_modules/*' \
    -not -path '*/dist/*' \
    -not -path '*/build/*' \
    -not -path '*/coverage/*' \
    -not -path '*/runtime/*' \
    -print0)
done

if [[ "$FOUND" -ne 0 ]]; then
  echo "link-boundary-scan: FAIL"
  exit 1
fi

echo "link-boundary-scan: PASS"
exit 0
