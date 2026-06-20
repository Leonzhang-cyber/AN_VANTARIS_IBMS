#!/usr/bin/env python3
"""Generate the airport Operations Console Handoff Gate artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.operations_console_handoff_gate import build_airport_operations_console_handoff_gate

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-operations-console-handoff-gate.v1.json"


def main() -> int:
    gate = build_airport_operations_console_handoff_gate()
    OUTPUT.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("AIRPORT_CONSOLE_PACKAGE_HANDOFF_GATE_COMPLETE")
    print("AIRPORT_CONSOLE_PACKAGE_READY_FOR_API_FRONTEND_PLANNING")
    print("ONE_AIRPORT_A5_02_AIRPORT_CONSOLE_PACKAGE_READINESS_AND_HANDOFF_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
