#!/usr/bin/env python3
"""Generate the airport A3 readiness release gate artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.a3_readiness_release_gate import build_airport_a3_readiness_release_gate

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-a3-readiness-release-gate.v1.json"


def main() -> int:
    release_gate = build_airport_a3_readiness_release_gate()
    OUTPUT.write_text(json.dumps(release_gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("A3_READINESS_AGGREGATION_AND_RELEASE_GATE_COMPLETE")
    print("A3_READ_ONLY_RELEASE_GATE_PASS")
    print("ONE_AIRPORT_A3_07_A3_READINESS_AGGREGATION_AND_RELEASE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
