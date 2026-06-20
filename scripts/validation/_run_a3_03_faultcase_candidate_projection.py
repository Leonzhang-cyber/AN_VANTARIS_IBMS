#!/usr/bin/env python3
"""Generate deterministic A3-03 airport UFMS FaultCase candidate projection."""
from __future__ import annotations

from pathlib import Path

from industry_profiles.airport.faultcase_candidate_projection import write_airport_faultcase_candidate_projection

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-faultcase-candidates.v1.json"


def main() -> int:
    projection = write_airport_faultcase_candidate_projection(OUTPUT)
    print(projection["implementationStatus"])
    print(projection["readinessOutcome"])
    print("ONE_AIRPORT_A3_03_UFMS_FAULTCASE_CANDIDATE_FIXTURE_GENERATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
