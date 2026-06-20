#!/usr/bin/env python3
"""Generate the airport read-only frontend skeleton artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.read_only_frontend_skeleton import build_airport_read_only_frontend_skeleton

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-frontend-skeleton.v1.json"


def main() -> int:
    skeleton = build_airport_read_only_frontend_skeleton()
    OUTPUT.write_text(json.dumps(skeleton, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("READ_ONLY_FRONTEND_SKELETON_FOUNDATION_COMPLETE")
    print("READ_ONLY_FRONTEND_SKELETON_READY_FOR_FUTURE_UI_IMPLEMENTATION")
    print("ONE_AIRPORT_A8_01_READ_ONLY_FRONTEND_SKELETON_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
