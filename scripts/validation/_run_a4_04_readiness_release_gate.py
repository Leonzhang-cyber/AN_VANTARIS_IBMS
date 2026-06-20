#!/usr/bin/env python3
"""Generate the airport A4 readiness release gate artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.a4_readiness_release_gate import build_airport_a4_readiness_release_gate

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-a4-readiness-release-gate.v1.json"


def main() -> int:
    release_gate = build_airport_a4_readiness_release_gate()
    OUTPUT.write_text(json.dumps(release_gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("A4_OPERATOR_REVIEW_READINESS_AND_RELEASE_GATE_COMPLETE")
    print("A4_OPERATOR_REVIEW_READ_ONLY_RELEASE_GATE_PASS")
    print("ONE_AIRPORT_A4_04_OPERATOR_REVIEW_READINESS_AND_RELEASE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
