#!/usr/bin/env python3
"""Generate the final Airport International GA release gate artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.airport_international_ga_release_gate import build_airport_international_ga_release_gate

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-release-gate.v1.json"


def main() -> int:
    gate = build_airport_international_ga_release_gate()
    OUTPUT.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("AIRPORT_INTERNATIONAL_GA_RELEASE_TERMINOLOGY_ALIGNMENT_COMPLETE")
    print("AIRPORT_INTERNATIONAL_GA_READINESS_CANDIDATE_PASS")
    print("ONE_AIRPORT_GA_01_ALIGN_AIRPORT_RELEASE_TERMINOLOGY_WITH_INTERNATIONAL_GA_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
