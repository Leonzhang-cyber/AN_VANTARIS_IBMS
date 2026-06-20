#!/usr/bin/env python3
"""Generate the final Airport read-only POC release gate artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.airport_read_only_poc_release_gate import build_airport_read_only_poc_release_gate

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-poc-release-gate.v1.json"


def main() -> int:
    gate = build_airport_read_only_poc_release_gate()
    OUTPUT.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("AIRPORT_READ_ONLY_POC_RELEASE_AGGREGATION_AND_FINAL_GATE_COMPLETE")
    print("AIRPORT_READ_ONLY_POC_RELEASE_CANDIDATE_PASS")
    print("ONE_AIRPORT_A9_01_AIRPORT_READ_ONLY_POC_RELEASE_AGGREGATION_AND_FINAL_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
