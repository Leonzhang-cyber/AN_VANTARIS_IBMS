#!/usr/bin/env bash
set -euo pipefail

MODE="dry-run"
if [[ "${1:-}" == "--execute" ]]; then
  MODE="execute"
fi

echo "VANTARIS ONE Customer Delivery install plan"
echo "Requested mode: ${MODE}"
echo "Default mode is dry-run. No root escalation, service manager calls, dependency installation, migration tooling, DB write, service start, or runtime activation is performed."

echo "Planned actions if future execution is approved:"
echo "1. Confirm signed customer deployment window."
echo "2. Import offline package into approved target layout."
echo "3. Verify EDGE/LINK/DB/Contracts package integrity."
echo "4. Stage configuration placeholders without secrets."
echo "5. Wait for explicit production activation approval."

if [[ "${MODE}" == "execute" ]]; then
  echo "EXECUTE_NOT_IMPLEMENTED_IN_R9_SCAFFOLD"
  exit 2
fi

echo "INSTALL_CUSTOMER_DELIVERY_DRY_RUN_ONLY_PASS"
