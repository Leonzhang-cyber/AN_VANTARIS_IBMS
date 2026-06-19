#!/usr/bin/env python3
"""Run airport asset Excel intake against operator-supplied workbook."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--airport-context-id", required=True)
    parser.add_argument("--terminal-context-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--check")
    parser.add_argument("--fail-on-blocker", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = Path(args.root).resolve()
    backend_src = root / "AN_VANTARIS_IBMS-backend"
    if str(backend_src) not in sys.path:
        sys.path.insert(0, str(backend_src))

    from src.asset_graph.airport_intake import AirportIntakeError, compare_deterministic_outputs, run_airport_asset_excel_intake

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not input_path.is_file():
        print("ONE_AIRPORT_A1_01_WAITING_FOR_SOURCE_WORKBOOK")
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = run_airport_asset_excel_intake(
            input_path=input_path,
            output_dir=output_dir,
            airport_context_id=args.airport_context_id,
            terminal_context_id=args.terminal_context_id,
            run_id=args.run_id,
            fail_on_blocker=args.fail_on_blocker,
            fail_on_review=args.fail_on_review,
        )
    except AirportIntakeError as exc:
        print(f"ONE_AIRPORT_ASSET_EXCEL_INTAKE_FAIL: {exc.code}")
        return 3

    if args.check:
        expected = Path(args.check).resolve()
        actual = output_dir / "airport-asset-intake-evidence.json"
        ok, reason = compare_deterministic_outputs(expected, actual)
        if not ok:
            print(f"ONE_AIRPORT_ASSET_EXCEL_INTAKE_CHECK_FAIL: {reason}")
            return 4
        print(f"ONE_AIRPORT_ASSET_EXCEL_INTAKE_CHECK_PASS: {reason}")

    print("ONE_AIRPORT_ASSET_EXCEL_INTAKE_RUN_PASS")
    print(f"READINESS_OUTCOME={result['readinessOutcome']}")
    print(f"RESULT_DIGEST={result['resultDigest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
