#!/usr/bin/env python3
"""Generate the airport read-only frontend implementation release gate artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.read_only_frontend_release_gate import build_airport_read_only_frontend_release_gate

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-frontend-implementation-release-gate.v1.json"


def main() -> int:
    gate = build_airport_read_only_frontend_release_gate()
    OUTPUT.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("READ_ONLY_FRONTEND_IMPLEMENTATION_RELEASE_GATE_COMPLETE")
    print("READ_ONLY_FRONTEND_READY_FOR_FUTURE_UI_IMPLEMENTATION")
    print("ONE_AIRPORT_A8_03_READ_ONLY_FRONTEND_IMPLEMENTATION_RELEASE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
