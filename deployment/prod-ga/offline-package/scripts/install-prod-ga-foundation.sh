#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
MANIFEST_PATH="$ROOT_DIR/deployment/prod-ga/offline-package/manifest/prod-ga-foundation-package-manifest.v1.json"
MODE="dry-run"

if [[ "${1:-}" == "--execute" ]]; then
  MODE="execute-requested"
fi

echo "[ONE-PROD-GA-R4] Production GA foundation package install scaffold"
echo "mode=$MODE"
echo "manifest=$MANIFEST_PATH"
echo
echo "Planned actions:"
echo "1. Verify manifest exists."
echo "2. Verify referenced foundation packages exist: EDGE, LINK, DB, Contracts."
echo "3. Verify forbidden files are absent."
echo "4. Prepare operator handoff checklist."
echo
echo "Safety:"
echo "- EDGE start: false"
echo "- LINK start: false"
echo "- DB migration execution: false"
echo "- DB write: false"
echo "- runtime activation: false"
echo "- install scripts execution: false in default dry-run mode"

if [[ "$MODE" == "execute-requested" ]]; then
  echo
  echo "Execution was explicitly requested, but R4 is a scaffold-only package."
  echo "No install actions are implemented or executed by this script."
  exit 2
fi

echo
echo "Dry-run complete. No files changed."

