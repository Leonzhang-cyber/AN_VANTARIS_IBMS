#!/usr/bin/env python3
"""Generate Airport International GA handoff notes."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.international_ga_handoff_notes import build_airport_international_ga_handoff_notes

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-international-ga-handoff-notes.v1.json"


def main() -> int:
    notes = build_airport_international_ga_handoff_notes()
    OUTPUT.write_text(json.dumps(notes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_COMPLETE")
    print("INTERNATIONAL_GA_HANDOFF_NOTES_READY_FOR_STAKEHOLDER_AND_ENGINEERING_HANDOFF")
    print("ONE_AIRPORT_GA_03_INTERNATIONAL_GA_HANDOFF_NOTES_AND_RELEASE_NOTES_FREEZE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
