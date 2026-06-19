"""Load versioned read migration readiness policy registry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

DEFAULT_POLICY_RELATIVE = (
    "AN_VANTARIS_ONE/registries/asset-graph-read-migration-readiness-policy.v1.json"
)


class ReadinessPolicyError(ValueError):
    """Invalid readiness policy registry."""


def load_readiness_policy(path: Path | None = None, *, root: Path | None = None) -> dict[str, Any]:
    if path is None:
        if root is None:
            raise ReadinessPolicyError("policy path or repository root is required")
        path = root / DEFAULT_POLICY_RELATIVE
    if not path.is_file():
        raise ReadinessPolicyError(f"policy registry not found: {path}")
    policy = json.loads(path.read_text(encoding="utf-8"))
    _validate_policy(policy)
    from .semantics import validate_gate_semantics

    validate_gate_semantics(policy)
    return policy


def _validate_policy(policy: Mapping[str, Any]) -> None:
    required = ("policyName", "policyVersion", "authority", "allowedDecisions", "forbiddenDecisions")
    missing = [key for key in required if key not in policy]
    if missing:
        raise ReadinessPolicyError(f"policy missing keys: {', '.join(missing)}")
    if "READY_FOR_WRITE_CUTOVER" not in policy["forbiddenDecisions"]:
        raise ReadinessPolicyError("policy must forbid READY_FOR_WRITE_CUTOVER")
