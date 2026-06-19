#!/usr/bin/env python3
"""Validate canonical Asset Graph persistence contract."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "AN_VANTARIS_ONE/registries/asset-graph-persistence-contract.v1.json"
MODULE_DIR = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/persistence_contract"
TEST_DIR = ROOT / "AN_VANTARIS_IBMS-backend/tests/asset_graph/persistence_contract"

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/registries/asset-graph-persistence-contract.v1.json",
    "AN_VANTARIS_IBMS-backend/src/asset_graph/persistence_contract/",
    "AN_VANTARIS_IBMS-backend/tests/asset_graph/persistence_contract/",
    "scripts/validation/validate-one-asset-graph-persistence-contract.py",
)

FORBIDDEN_IMPORTS = ("sqlalchemy", "db.session", "create_app(", "@api_bp.route", "flask")
FORBIDDEN_SQL = ("CREATE TABLE", "INSERT INTO", "ALTER TABLE", "SELECT * FROM")
FORBIDDEN_ROOTS = ("AN_VANTARIS_IBMS-frontend/", "UFMS", "EDGE", "LINK", "UMMS", "UCore", "UConsole")


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

    checks.append(("Contract registry exists", CONTRACT.is_file()))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8")) if CONTRACT.is_file() else {}
    if contract:
        checks.append(("Contract versioned", contract.get("contractVersion") == "1.0.0"))
        checks.append(("Contract only implementation", contract.get("implementationStatus") == "CONTRACT_ONLY"))
        checks.append(("Write cutover prohibited", contract.get("writeCutoverStatus") == "NOT_READY_FOR_WRITE_CUTOVER"))
        checks.append(("Synthetic write prohibited", contract.get("syntheticWriteAuthorizationProhibited") is True))
        caps = contract.get("providerCapabilityDefaults", {})
        checks.append(("Provider writes disabled", caps.get("enabledForCanonicalWrites") is False))

    for token in FORBIDDEN_IMPORTS:
        if token.lower() in text.lower():
            errors.append(f"forbidden runtime pattern: {token}")
    for token in FORBIDDEN_SQL:
        if token in text:
            errors.append(f"forbidden SQL pattern: {token}")

    for required in (
        "CanonicalDeviceProvider",
        "AssetGraphUnitOfWork",
        "AssetGraphPersistenceCoordinator",
        "CreateCanonicalDevice",
        "PersistenceAuthorizationResult",
        "IDEMPOTENCY_CONFLICT",
        "NOT_READY_FOR_WRITE_CUTOVER",
    ):
        if required not in text:
            errors.append(f"missing required pattern: {required}")

    sys.path.insert(0, str(ROOT / "AN_VANTARIS_IBMS-backend"))
    from src.asset_graph.persistence_contract import (
        AUTHORIZATION_DENIED,
        default_provider_capabilities,
        evaluate_persistence_authorization,
    )
    from src.asset_graph.persistence_contract.authorization import PersistenceAuthorizationInput

    checks.append(("Default provider writes disabled", not default_provider_capabilities().enabled_for_canonical_writes))
    synthetic = evaluate_persistence_authorization(
        PersistenceAuthorizationInput(
            evidence_classification="SYNTHETIC_REPRESENTATIVE_ONLY",
            readiness_decision="NOT_READY",
            hard_blocker_count=0,
            evidence_digest="a" * 64,
            readiness_result_digest="b" * 64,
            execution_result_digest="c" * 64,
            tenant_scope="tenant-a",
            site_scope="site-a",
            source_system_scope="legacy-device-v1",
            mapping_version="legacy-device-v1",
            requested_evidence_digest="a" * 64,
            requested_readiness_result_digest="b" * 64,
            requested_execution_result_digest="c" * 64,
            requested_tenant_id="tenant-a",
            requested_site_id="site-a",
            requested_source_system_id="legacy-device-v1",
            requested_mapping_version="legacy-device-v1",
            persistence_approval_granted=False,
            approved_execution_contract_present=True,
            provider_capabilities=default_provider_capabilities(),
        )
    )
    checks.append(("Synthetic evidence cannot authorize writes", synthetic.decision == AUTHORIZATION_DENIED))

    unit = _run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(TEST_DIR),
            "-p",
            "test*.py",
        ],
        env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")},
    )
    checks.append(("Focused persistence contract tests", unit.returncode == 0))
    if unit.returncode != 0:
        errors.append(unit.stderr or unit.stdout)

    changed = _changed_paths()
    if changed:
        disallowed = [
            path
            for path in changed
            if path
            and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)
        ]
        if disallowed:
            errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")

    for forbidden_root in FORBIDDEN_ROOTS:
        if any(path.startswith(forbidden_root) for path in changed):
            errors.append(f"forbidden root touched: {forbidden_root}")

    print("ONE Asset Graph Persistence Contract Validation")
    print("=" * 60)
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nONE_ASSET_GRAPH_PERSISTENCE_CONTRACT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
