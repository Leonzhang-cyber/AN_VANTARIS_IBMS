#!/usr/bin/env python3
"""Generate deterministic A3-02 airport alarm/event asset resolution review projection."""
from __future__ import annotations

from pathlib import Path

from industry_profiles.airport.alarm_event_asset_resolution_projection import (
    write_airport_alarm_event_asset_resolution_projection,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-alarm-event-asset-resolution-review.v1.json"
)


def main() -> int:
    projection = write_airport_alarm_event_asset_resolution_projection(OUTPUT)
    print(projection["implementationStatus"])
    print(projection["readinessOutcome"])
    print("ONE_AIRPORT_A3_02_ALARM_EVENT_ASSET_RESOLUTION_FIXTURE_GENERATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
