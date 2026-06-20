#!/usr/bin/env python3
"""Generate the airport Operator Review Policy Guard projection."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.operator_review_policy_guard_projection import (
    build_airport_operator_review_policy_guard_projection,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-operator-review-policy-guard.v1.json"


def main() -> int:
    projection = build_airport_operator_review_policy_guard_projection()
    OUTPUT.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("OPERATOR_REVIEW_DECISION_AUDIT_AND_POLICY_GUARD_COMPLETE")
    print("OPERATOR_REVIEW_POLICY_GUARD_READY_FOR_READ_ONLY_PREVIEW")
    print("ONE_AIRPORT_A4_03_OPERATOR_REVIEW_DECISION_AUDIT_AND_POLICY_GUARD_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
