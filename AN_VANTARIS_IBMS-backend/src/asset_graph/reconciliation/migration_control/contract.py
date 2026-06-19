"""Load versioned read migration execution contract registry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

DEFAULT_CONTRACT_RELATIVE = (
    "AN_VANTARIS_ONE/registries/asset-graph-read-migration-execution-contract.v1.json"
)


class MigrationControlContractError(ValueError):
    """Invalid read migration execution contract registry."""


def load_execution_contract(path: Path | None = None, *, root: Path | None = None) -> dict[str, Any]:
    if path is None:
        if root is None:
            raise MigrationControlContractError("contract path or repository root is required")
        path = root / DEFAULT_CONTRACT_RELATIVE
    if not path.is_file():
        raise MigrationControlContractError(f"execution contract not found: {path}")
    contract = json.loads(path.read_text(encoding="utf-8"))
    _validate_contract(contract)
    return contract


def _validate_contract(contract: Mapping[str, Any]) -> None:
    required = (
        "contractName",
        "contractVersion",
        "authority",
        "executionMode",
        "allowedExecutionStates",
        "forbiddenExecutionStates",
        "allowedOperations",
        "forbiddenOperations",
        "preconditionGates",
        "writeCutoverStatus",
    )
    missing = [key for key in required if key not in contract]
    if missing:
        raise MigrationControlContractError(f"contract missing keys: {', '.join(missing)}")
    if contract.get("executionMode") != "READ_ONLY_VALIDATION":
        raise MigrationControlContractError("executionMode must be READ_ONLY_VALIDATION")
    if contract.get("writeCutoverStatus") != "NOT_READY_FOR_WRITE_CUTOVER":
        raise MigrationControlContractError("writeCutoverStatus must remain NOT_READY_FOR_WRITE_CUTOVER")
    forbidden_states = set(contract.get("forbiddenExecutionStates", ()))
    for state in ("APPROVED_FOR_WRITE_MIGRATION", "APPROVED_FOR_WRITE_CUTOVER", "DUAL_WRITE_ACTIVE"):
        if state not in forbidden_states:
            raise MigrationControlContractError(f"forbidden execution state missing: {state}")
    if "APPROVE_WRITE_CUTOVER" not in contract.get("forbiddenOperations", ()):
        raise MigrationControlContractError("APPROVE_WRITE_CUTOVER must be forbidden")
    if contract.get("syntheticProductionMigrationProhibited") is not True:
        raise MigrationControlContractError("synthetic production migration must be prohibited")
