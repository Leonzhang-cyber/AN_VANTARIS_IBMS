#!/usr/bin/env python3
"""Generate deterministic A3-05 airport Evidence Investigation projection."""
from __future__ import annotations

from pathlib import Path

from industry_profiles.airport.evidence_investigation_projection import write_airport_evidence_investigation_projection

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-evidence-investigation.v1.json"


def main() -> int:
    projection = write_airport_evidence_investigation_projection(OUTPUT)
    print(projection["implementationStatus"])
    print(projection["readinessOutcome"])
    print("ONE_AIRPORT_A3_05_EVIDENCE_INVESTIGATION_FIXTURE_GENERATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
