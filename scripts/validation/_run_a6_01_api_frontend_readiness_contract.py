#!/usr/bin/env python3
"""Generate the airport API / Frontend readiness contract artifact."""
from __future__ import annotations

import json
from pathlib import Path

from industry_profiles.airport.api_frontend_readiness_contract import build_airport_api_frontend_readiness_contract

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-api-frontend-readiness-contract.v1.json"


def main() -> int:
    contract = build_airport_api_frontend_readiness_contract()
    OUTPUT.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("API_FRONTEND_READINESS_CONTRACT_FREEZE_COMPLETE")
    print("API_FRONTEND_CONTRACT_FROZEN_FOR_FUTURE_IMPLEMENTATION_PLANNING")
    print("ONE_AIRPORT_A6_01_API_FRONTEND_READINESS_CONTRACT_FREEZE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
