#!/usr/bin/env python3
"""Generate the airport Operator Review Decision Layer projection."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.operator_review_decision_projection import build_airport_operator_review_decision_projection

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-operator-review-decisions.v1.json"


def main() -> int:
    projection = build_airport_operator_review_decision_projection()
    OUTPUT.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("OPERATOR_REVIEW_DECISION_LAYER_FOUNDATION_COMPLETE")
    print("OPERATOR_REVIEW_DECISION_QUEUE_COMPLETE_PENDING_OPERATOR_ACTION")
    print("ONE_AIRPORT_A4_01_OPERATOR_REVIEW_DECISION_LAYER_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
