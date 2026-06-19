#!/usr/bin/env python3
"""Run offline limited read validation execution."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--readiness", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--evaluation-instant", required=True)
    parser.add_argument("--check")
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = Path(args.root).resolve()
    backend_src = root / "AN_VANTARIS_IBMS-backend"
    if str(backend_src) not in sys.path:
        sys.path.insert(0, str(backend_src))

    from src.asset_graph.reconciliation.read_validation import ExecutionRequest, execute_limited_read_validation

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    readiness = json.loads(Path(args.readiness).read_text(encoding="utf-8"))
    scope = plan.get("scopeSummary", {})
    request = ExecutionRequest(
        root=str(root),
        plan_path=str(Path(args.plan).resolve()),
        evidence_path=str(Path(args.evidence).resolve()),
        readiness_path=str(Path(args.readiness).resolve()),
        output_dir=str(Path(args.output_dir).resolve()),
        run_id=args.run_id,
        evaluation_instant=args.evaluation_instant,
        evidence_digest=str(readiness.get("evidenceDigest", "")),
        readiness_result_digest=str(readiness.get("resultDigest", "")),
        scope_digest=str(scope.get("scopeDigest", "")),
        mapping_version=str(scope.get("mappingVersion", "")),
    )
    result = execute_limited_read_validation(request).serialize()
    print(json.dumps(result, indent=2, sort_keys=True))

    if args.check:
        expected = Path(args.check).resolve()
        actual = Path(args.output_dir).resolve() / "execution-result.json"
        if expected.read_bytes() != actual.read_bytes():
            print("ONE_ASSET_GRAPH_OFFLINE_READ_VALIDATION_CHECK_FAIL")
            return 3
        print("ONE_ASSET_GRAPH_OFFLINE_READ_VALIDATION_CHECK_PASS")

    if result["validationOutcome"] == "EXECUTION_BLOCKED":
        print("ONE_ASSET_GRAPH_OFFLINE_READ_VALIDATION_BLOCKED")
        return 2
    if result["validationOutcome"] == "VALIDATION_FAILED":
        print("ONE_ASSET_GRAPH_OFFLINE_READ_VALIDATION_FAILED")
        return 4
    print("ONE_ASSET_GRAPH_OFFLINE_READ_VALIDATION_RUN_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
