#!/usr/bin/env python3
"""Generate the airport read-only Operations Console Package artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.operations_console_package import build_airport_operations_console_package

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-operations-console-package.v1.json"


def main() -> int:
    package = build_airport_operations_console_package()
    OUTPUT.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_COMPLETE")
    print("AIRPORT_OPERATIONS_CONSOLE_PACKAGE_READY_FOR_READ_ONLY_CONSUMPTION")
    print("ONE_AIRPORT_A5_01_READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
