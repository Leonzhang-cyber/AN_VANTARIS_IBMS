#!/usr/bin/env python3
"""Run synthetic Excel legacy device reconciliation evidence intake."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--check")
    parser.add_argument("--allow-run-id-only-diff", action="store_true")
    parser.add_argument("--fail-on-blocker", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    parser.add_argument("--skip-fixture-profile", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = Path(args.root).resolve()
    backend_src = root / "AN_VANTARIS_IBMS-backend"
    if str(backend_src) not in sys.path:
        sys.path.insert(0, str(backend_src))

    from src.asset_graph.reconciliation.evidence import compare_evidence_reports
    from src.asset_graph.reconciliation.evidence.excel import (
        ExcelIntakeError,
        run_excel_evidence_intake,
    )

    input_path = Path(args.input).resolve()
    json_output = Path(args.json_output).resolve()
    report_output = Path(args.report_output).resolve()
    json_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.parent.mkdir(parents=True, exist_ok=True)

    try:
        intake = run_excel_evidence_intake(
            root=root,
            input_path=input_path,
            json_output=json_output,
            report_output=report_output,
            run_id=args.run_id,
            enforce_fixture_profile=not args.skip_fixture_profile,
            fail_on_blocker=args.fail_on_blocker,
            fail_on_review=args.fail_on_review,
        )
    except ExcelIntakeError as exc:
        print(f"ONE_DEVICE_RECONCILIATION_EXCEL_FAIL: {exc.code}")
        return 2

    for item in intake.get("rejectedSampleResults", []):
        print(
            "REJECTED_SAMPLE "
            f"category={item['category']} "
            f"field={item['fieldName']} "
            f"status={item['rejectionStatus']} "
            f"path={item['packagePath']}"
        )

    if args.check:
        expected = Path(args.check).resolve()
        ok, reason = compare_evidence_reports(
            expected_path=expected,
            actual_path=report_output,
            allow_run_id_only_diff=args.allow_run_id_only_diff,
        )
        if not ok:
            print(f"ONE_DEVICE_RECONCILIATION_EXCEL_CHECK_FAIL: {reason}")
            return 3
        print(f"ONE_DEVICE_RECONCILIATION_EXCEL_CHECK_PASS: {reason}")

    print("ONE_DEVICE_RECONCILIATION_EXCEL_RUN_PASS")
    print(f"WRITE_CUTOVER_STATUS={intake['writeCutoverStatus']}")
    print(f"SYNTHETIC_ASSESSMENT={intake['syntheticAssessment']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
