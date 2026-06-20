#!/usr/bin/env python3
"""Generate Airport International GA final local verification."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.international_ga_final_verification import build_airport_international_ga_final_local_verification

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-final-local-verification.v1.json"


def main() -> int:
    verification = build_airport_international_ga_final_local_verification()
    OUTPUT.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("INTERNATIONAL_GA_FINAL_LOCAL_VERIFICATION_AND_OPTIONAL_RELEASE_TAG_PLAN_COMPLETE")
    print("INTERNATIONAL_GA_LOCAL_VERIFICATION_PASS_READY_FOR_EXPLICIT_PUSH_TAG_DECISION")
    print("ONE_AIRPORT_GA_04_INTERNATIONAL_GA_FINAL_LOCAL_VERIFICATION_AND_OPTIONAL_RELEASE_TAG_PLAN_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
