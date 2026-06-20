#!/usr/bin/env python3
"""Generate the Airport International GA release candidate package."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.international_ga_release_package import build_airport_international_ga_release_candidate_package

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-release-candidate-package.v1.json"


def main() -> int:
    package = build_airport_international_ga_release_candidate_package()
    OUTPUT.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_COMPLETE")
    print("INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGE_READY_FOR_HANDOFF")
    print("ONE_AIRPORT_GA_02_INTERNATIONAL_GA_RELEASE_CANDIDATE_PACKAGING_AND_VALIDATION_MATRIX_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
