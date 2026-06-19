"""Load versioned canonical persistence contract registry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .constants import (
    CONTRACT_NAME,
    CONTRACT_VERSION,
    IMPLEMENTATION_STATUS,
    WRITE_CUTOVER_STATUS,
    DEFAULT_CONTRACT_RELATIVE,
    CONFLICT_CODES,
    FORBIDDEN_AUTHORIZATION_DECISIONS,
)
from .errors import PersistenceContractError


def load_persistence_contract(path: Path | None = None, *, root: Path | None = None) -> dict[str, Any]:
    if path is None:
        if root is None:
            raise PersistenceContractError("contract path or repository root is required")
        path = root / DEFAULT_CONTRACT_RELATIVE
    if not path.is_file():
        raise PersistenceContractError(f"persistence contract not found: {path}")
    contract = json.loads(path.read_text(encoding="utf-8"))
    validate_persistence_contract(contract)
    return contract


def validate_persistence_contract(contract: Mapping[str, Any]) -> None:
    required = (
        "contractName",
        "contractVersion",
        "authority",
        "implementationStatus",
        "writeCutoverStatus",
        "batchLimits",
        "conflictCodes",
        "allowedAuthorizationDecisions",
        "forbiddenAuthorizationDecisions",
    )
    missing = [key for key in required if key not in contract]
    if missing:
        raise PersistenceContractError(f"contract missing keys: {', '.join(missing)}")
    if contract.get("contractName") != CONTRACT_NAME:
        raise PersistenceContractError("contractName mismatch")
    if contract.get("contractVersion") != CONTRACT_VERSION:
        raise PersistenceContractError("contractVersion mismatch")
    if contract.get("implementationStatus") != IMPLEMENTATION_STATUS:
        raise PersistenceContractError("implementationStatus must be CONTRACT_ONLY")
    if contract.get("writeCutoverStatus") != WRITE_CUTOVER_STATUS:
        raise PersistenceContractError("writeCutoverStatus must remain NOT_READY_FOR_WRITE_CUTOVER")
    registry_conflicts = set(contract.get("conflictCodes", ()))
    if not CONFLICT_CODES.issubset(registry_conflicts):
        raise PersistenceContractError("conflictCodes registry incomplete")
    forbidden = set(contract.get("forbiddenAuthorizationDecisions", ()))
    if not FORBIDDEN_AUTHORIZATION_DECISIONS.issubset(forbidden):
        raise PersistenceContractError("forbidden authorization decisions incomplete")
    if contract.get("syntheticWriteAuthorizationProhibited") is not True:
        raise PersistenceContractError("synthetic write authorization must be prohibited")
    limits = contract.get("batchLimits", {})
    for key, expected in (
        ("maximumDevicesPerUnitOfWork", 100),
        ("maximumPointsPerDevice", 5000),
        ("maximumRelationshipsPerUnitOfWork", 10000),
        ("maximumTagsPerUnitOfWork", 1000),
        ("maximumCommandsPerBatch", 20000),
    ):
        if limits.get(key) != expected:
            raise PersistenceContractError(f"batch limit {key} must be {expected}")


def batch_limits(contract: Mapping[str, Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in dict(contract.get("batchLimits", {})).items()}
