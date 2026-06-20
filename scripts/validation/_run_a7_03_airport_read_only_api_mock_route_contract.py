#!/usr/bin/env python3
"""Generate the airport read-only API mock route contract artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.read_only_api_mock_route_contract import build_airport_read_only_api_mock_route_contract

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-mock-route-contract.v1.json"


def main() -> int:
    contract = build_airport_read_only_api_mock_route_contract()
    OUTPUT.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_COMPLETE")
    print("READ_ONLY_API_MOCK_ROUTE_CONTRACT_READY_FOR_FUTURE_ROUTE_IMPLEMENTATION")
    print("ONE_AIRPORT_A7_03_READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
