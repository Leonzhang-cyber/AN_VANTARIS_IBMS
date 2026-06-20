#!/usr/bin/env python3
"""Generate deterministic A3-04 airport WorkOrderIntent candidate projection."""
from __future__ import annotations

from pathlib import Path

from industry_profiles.airport.workorder_intent_candidate_projection import (
    write_airport_workorder_intent_candidate_projection,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-workorder-intent-candidates.v1.json"


def main() -> int:
    projection = write_airport_workorder_intent_candidate_projection(OUTPUT)
    print(projection["implementationStatus"])
    print(projection["readinessOutcome"])
    print("ONE_AIRPORT_A3_04_WORKORDER_INTENT_CANDIDATE_FIXTURE_GENERATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
