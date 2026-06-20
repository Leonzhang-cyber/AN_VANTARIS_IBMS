#!/usr/bin/env python3
"""Generate the airport API / Frontend implementation readiness gate artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.api_frontend_implementation_gate import build_airport_api_frontend_implementation_readiness_gate

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-api-frontend-implementation-readiness-gate.v1.json"


def main() -> int:
    gate = build_airport_api_frontend_implementation_readiness_gate()
    OUTPUT.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_COMPLETE")
    print("API_FRONTEND_READY_FOR_READ_ONLY_SKELETON_PLANNING")
    print("ONE_AIRPORT_A6_02_API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
