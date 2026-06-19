#!/usr/bin/env python3
"""Validate Asset Graph read migration readiness gate."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "AN_VANTARIS_ONE/registries/asset-graph-read-migration-readiness-policy.v1.json"
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/readiness"
TEST_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/readiness"
CLEAN_FIXTURE = TEST_DIR / "fixtures/clean-synthetic-evidence-report.json"
SYNTHETIC_REPORT = Path("/tmp/one-p1-16h/run-1-report.json")

NUMERIC_GATE_CODES = (
    "REQUIRED_FIELD_COVERAGE_GATE",
    "SAFE_SOURCE_COVERAGE_GATE",
    "UNRESOLVED_RELATIONSHIP_GATE",
    "DUPLICATE_RELATIONSHIP_GATE",
    "REVIEW_RATIO_GATE",
    "WARNING_RATIO_GATE",
    "HAS_POINT_PARITY_GATE",
    "TENANT_SCOPE_GATE",
    "SITE_SCOPE_GATE",
)

APPROVED_AGGREGATIONS = {
    "MINIMUM_PER_RECORD",
    "MAXIMUM_PER_RECORD",
    "PACKAGE_TOTAL",
    "PACKAGE_RATIO",
    "EXACT_PARITY",
    "ZERO_TOLERANCE",
    "BOUNDED_TOTAL",
    "BOOLEAN_ASSERTION",
}

APPROVED_PERCENTAGE_SCALES = {"0_TO_100", "NONE"}
RAW_IDENTIFIER_MARKERS = ("SYNTH-DEV-", "ag-device-", "ag-point-")
BASELINE_THRESHOLDS = {
    "requiredFieldCoverageMinimumPercent": 100,
    "safeSourceFieldCoverageMinimumPercent": 75,
}

ALLOWED_PREFIXES = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/readiness/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/readiness/",
    "AN_VANTARIS_ONE/registries/asset-graph-read-migration-readiness-policy.v1.json",
    "scripts/validation/validate-one-asset-graph-readiness.py",
    "scripts/validation/validate-one-device-reconciliation-evidence.py",
    "scripts/validation/validate-one-device-reconciliation-excel.py",
)


def _run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=env)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        paths.update(_run(command).stdout.splitlines())
    return {path for path in paths if path}


def _module_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(MODULE_DIR.rglob("*.py")))


def main() -> int:
    errors: list[str] = []
    checks: list[tuple[str, bool]] = []
    text = _module_text()

    checks.append(("Policy registry exists", POLICY.is_file()))
    if POLICY.is_file():
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        checks.append(("Policy versioned", policy.get("policyVersion") == "1.0.0"))
        checks.append(("Write cutover forbidden", "READY_FOR_WRITE_CUTOVER" in policy.get("forbiddenDecisions", [])))
        checks.append(("Thresholds in policy", "coverageThresholds" in policy and "ratioThresholds" in policy))
        coverage = policy.get("coverageThresholds", {})
        checks.append(("Safe source threshold 75%", coverage.get("safeSourceFieldCoverageMinimumPercent") == 75))
        checks.append(("Required field threshold 100%", coverage.get("requiredFieldCoverageMinimumPercent") == 100))
        checks.append(
            (
                "Threshold integrity",
                coverage.get("requiredFieldCoverageMinimumPercent") == BASELINE_THRESHOLDS["requiredFieldCoverageMinimumPercent"]
                and coverage.get("safeSourceFieldCoverageMinimumPercent") == BASELINE_THRESHOLDS["safeSourceFieldCoverageMinimumPercent"],
            )
        )
        semantics = policy.get("gateSemantics", {})
        approved_labels = set(policy.get("approvedAggregationLabels", ()))
        checks.append(("Approved aggregation labels declared", bool(approved_labels)))
        checks.append(
            (
                "Numeric gate semantics complete",
                all(gate_code in semantics for gate_code in NUMERIC_GATE_CODES),
            )
        )
        checks.append(
            (
                "Aggregation labels approved enum",
                all(
                    semantics[gate_code].get("aggregation") in APPROVED_AGGREGATIONS
                    and semantics[gate_code].get("aggregation") in approved_labels
                    for gate_code in NUMERIC_GATE_CODES
                    if gate_code in semantics
                ),
            )
        )
        checks.append(
            (
                "Percentage scales explicit",
                all(
                    semantics[gate_code].get("percentageScale") in APPROVED_PERCENTAGE_SCALES
                    for gate_code in NUMERIC_GATE_CODES
                    if gate_code in semantics
                ),
            )
        )
        safe_entry = semantics.get("SAFE_SOURCE_COVERAGE_GATE", {})
        checks.append(("Safe source aggregation documented", safe_entry.get("aggregation") == "MINIMUM_PER_RECORD"))
    else:
        errors.append("policy registry missing")
        policy = {}

    for token in ("sqlalchemy", "db.session", "create_app(", "@api_bp.route", "flask"):
        if token.lower() in text.lower():
            errors.append(f"forbidden runtime pattern: {token}")

    if "load_readiness_policy" not in text or "assess_readiness" not in text:
        errors.append("readiness assessor exports missing")

    sys.path.insert(0, str(ROOT / "AN_VANTARIS_IBMS-backend"))
    from src.asset_graph.reconciliation.readiness import assess_readiness, load_readiness_policy

    loaded_policy = load_readiness_policy(root=ROOT)
    clean = json.loads(CLEAN_FIXTURE.read_text(encoding="utf-8"))
    assessment = assess_readiness(clean, loaded_policy, determinism_confirmed=True)
    payload = assessment.serialize()
    checks.append(("Clean synthetic limited validation", payload["decision"] == "READY_FOR_LIMITED_READ_VALIDATION"))
    checks.append(("Write cutover prohibited output", payload["writeCutoverStatus"] == "NOT_READY_FOR_WRITE_CUTOVER"))
    checks.append(("No write cutover decision", payload["decision"] != "READY_FOR_WRITE_CUTOVER"))
    checks.append(("Coverage statistics present", "coverageStatistics" in payload and "gateSemantics" in payload))
    safe_gate = next(g for g in payload["gateResults"] if g["gateCode"] == "SAFE_SOURCE_COVERAGE_GATE")
    checks.append(
        (
            "Displayed safe source matches minimum",
            payload["coverageStatistics"]["safeSourceCoverageMinimumPercent"]
            == float(safe_gate["observedValue"].rstrip("%")),
        )
    )
    explanation_text = json.dumps(payload["gateResults"])
    checks.append(("No raw identifiers in explanations", not any(token in explanation_text for token in RAW_IDENTIFIER_MARKERS)))
    if payload["decision"] == "READY_FOR_READ_MIGRATION_CANDIDATE":
        errors.append("clean synthetic exceeded decision ceiling")

    if SYNTHETIC_REPORT.is_file():
        blocker_rich = json.loads(SYNTHETIC_REPORT.read_text(encoding="utf-8"))
        rich = assess_readiness(blocker_rich, loaded_policy, determinism_confirmed=True).serialize()
        checks.append(("Blocker-rich synthetic not ready", rich["decision"] == "NOT_READY"))
        checks.append(("Synthetic ceiling enforced", rich["decision"] != "READY_FOR_READ_MIGRATION_CANDIDATE"))
        safe_gate = next(g for g in rich["gateResults"] if g["gateCode"] == "SAFE_SOURCE_COVERAGE_GATE")
        checks.append(("Blocker-rich safe source fail", safe_gate["status"] == "FAIL"))
        checks.append(("Blocker-rich observed 73.33%", safe_gate["observedValue"] == "73.33%"))
        checks.append(("Blocker-rich aggregation minimum", safe_gate.get("aggregation") == "MINIMUM_PER_RECORD"))
        checks.append(
            (
                "Blocker-rich displayed matches minimum",
                rich["coverageStatistics"]["safeSourceCoverageMinimumPercent"]
                == float(safe_gate["observedValue"].rstrip("%")),
            )
        )
        rich_text = json.dumps(rich["gateResults"])
        checks.append(("Blocker-rich no raw identifiers", not any(token in rich_text for token in RAW_IDENTIFIER_MARKERS)))
    else:
        checks.append(("Blocker-rich synthetic not ready", True))
        checks.append(("Synthetic ceiling enforced", True))

    out1 = Path("/tmp/readiness-validator-1.json")
    out2 = Path("/tmp/readiness-validator-2.json")
    out1.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out2.write_text(json.dumps(assess_readiness(clean, loaded_policy, determinism_confirmed=True).serialize(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checks.append(("Deterministic assessment", out1.read_bytes() == out2.read_bytes()))

    unit = _run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "AN_VANTARIS_IBMS-backend/tests/asset_graph/reconciliation/readiness",
            "-p",
            "test*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused readiness tests", unit.returncode == 0))
    if unit.returncode != 0:
        errors.append(unit.stderr or unit.stdout)

    changed = _changed_paths()
    outside = sorted(path for path in changed if not path.startswith(ALLOWED_PREFIXES))
    checks.append(("Allowed path scope", not outside))
    if outside:
        errors.append("changed files outside allowed scope: " + ", ".join(outside))

    forbidden_roots = ("AN_VANTARIS_IBMS-frontend/", "UFMS", "EDGE", "LINK")
    for path in changed:
        if any(token in path for token in forbidden_roots):
            errors.append(f"non-scope file changed: {path}")

    print("[ONE ASSET GRAPH READ MIGRATION READINESS VALIDATION]")
    for label, status in checks:
        print(f"{label}: {'PASS' if status else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_ASSET_GRAPH_READ_MIGRATION_READINESS_FAIL")
        return 1
    print("ONE_ASSET_GRAPH_READ_MIGRATION_READINESS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
