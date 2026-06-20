#!/usr/bin/env python3
"""Generate the airport read-only API skeleton artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.read_only_api_skeleton import build_airport_read_only_api_skeleton

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-skeleton.v1.json"


def main() -> int:
    skeleton = build_airport_read_only_api_skeleton()
    OUTPUT.write_text(json.dumps(skeleton, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("READ_ONLY_API_SKELETON_FOUNDATION_COMPLETE")
    print("READ_ONLY_API_SKELETON_READY_FOR_FUTURE_IMPLEMENTATION")
    print("ONE_AIRPORT_A7_01_READ_ONLY_API_SKELETON_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
