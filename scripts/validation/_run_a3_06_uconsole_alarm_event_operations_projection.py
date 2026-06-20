#!/usr/bin/env python3
"""Generate the airport UConsole Alarm/Event Operations Projection."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.uconsole_alarm_event_operations_projection import (
    build_airport_uconsole_alarm_event_operations_projection,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-alarm-event-operations.v1.json"


def main() -> int:
    projection = build_airport_uconsole_alarm_event_operations_projection()
    OUTPUT.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_COMPLETE")
    print("UCONSOLE_ALARM_EVENT_OPERATIONS_READ_ONLY_PROJECTION_COMPLETE_PENDING_REVIEWS")
    print("ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
