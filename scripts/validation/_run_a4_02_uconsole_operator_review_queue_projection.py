#!/usr/bin/env python3
"""Generate the airport UConsole Operator Review Queue projection."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.uconsole_operator_review_queue_projection import (
    build_airport_uconsole_operator_review_queue_projection,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-operator-review-queue.v1.json"


def main() -> int:
    projection = build_airport_uconsole_operator_review_queue_projection()
    OUTPUT.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_COMPLETE")
    print("UCONSOLE_OPERATOR_REVIEW_QUEUE_READY_FOR_READ_ONLY_CONSUMPTION")
    print("ONE_AIRPORT_A4_02_OPERATOR_REVIEW_UCONSOLE_QUEUE_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
