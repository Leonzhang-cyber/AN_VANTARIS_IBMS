#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PYTHON="${IBMS_SMOKE_PYTHON:-python3}"
if [[ -x "$ROOT/.venv/bin/python" ]] && "$ROOT/.venv/bin/python" -c "import flask" 2>/dev/null; then
  PYTHON="$ROOT/.venv/bin/python"
elif [[ -x "/tmp/ibms-smoke-venv/bin/python" ]]; then
  PYTHON="/tmp/ibms-smoke-venv/bin/python"
fi

echo "Using Python: $PYTHON"
"$PYTHON" test/smoke/db_jwt_smoke.py
