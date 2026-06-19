#!/usr/bin/env python3
"""Run offline deterministic legacy device reconciliation evidence."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--format", choices=("json",), default="json")
    parser.add_argument("--check")
    parser.add_argument("--allow-run-id-only-diff", action="store_true")
    parser.add_argument("--fail-on-blocker", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = Path(args.root).resolve()
    backend_src = root / "AN_VANTARIS_IBMS-backend"
    if str(backend_src) not in sys.path:
        sys.path.insert(0, str(backend_src))
    from src.asset_graph.reconciliation.evidence import (  # noqa: WPS433
        EvidencePackageError,
        compare_evidence_reports,
        run_device_reconciliation_evidence,
    )

    input_path = (root / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        run_device_reconciliation_evidence(
            root=root,
            input_path=input_path,
            output_path=output_path,
            run_id=args.run_id,
            fail_on_blocker=args.fail_on_blocker,
            fail_on_review=args.fail_on_review,
        )
    except EvidencePackageError as exc:
        print(f"ONE_DEVICE_RECONCILIATION_EVIDENCE_FAIL: {exc.code}")
        return 2

    if args.check:
        expected = (root / args.check).resolve() if not Path(args.check).is_absolute() else Path(args.check).resolve()
        ok, reason = compare_evidence_reports(
            expected_path=expected,
            actual_path=output_path,
            allow_run_id_only_diff=args.allow_run_id_only_diff,
        )
        if not ok:
            print(f"ONE_DEVICE_RECONCILIATION_EVIDENCE_CHECK_FAIL: {reason}")
            return 3
        print(f"ONE_DEVICE_RECONCILIATION_EVIDENCE_CHECK_PASS: {reason}")

    print("ONE_DEVICE_RECONCILIATION_EVIDENCE_RUN_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
