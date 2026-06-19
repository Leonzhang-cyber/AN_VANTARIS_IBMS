"""Canonical identity and optimistic concurrency contract rules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from .conflicts import CONFLICT_MESSAGES
from .constants import UPDATE_OUTCOMES


@dataclass(frozen=True)
class CanonicalVersionMetadata:
    version: int
    created_revision: str
    updated_revision: str

    def serialize(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "createdRevision": self.created_revision,
            "updatedRevision": self.updated_revision,
        }


IMMUTABLE_IDENTITY_FIELDS = frozenset(
    {
        "canonicalGlobalId",
        "sourceIdentity",
        "tenantId",
        "pointParentDeviceGlobalId",
        "relationshipGlobalId",
        "tagKeyNamespace",
    }
)


def evaluate_update_version(
    *,
    current: Optional[CanonicalVersionMetadata],
    expected_version: int,
) -> str:
    if current is None:
        return "NOT_FOUND"
    if current.version != expected_version:
        return "VERSION_CONFLICT"
    return "UPDATED"


def validate_identity_immutability(
    *,
    object_type: str,
    existing: Mapping[str, Any],
    incoming: Mapping[str, Any],
) -> Optional[str]:
    for field in IMMUTABLE_IDENTITY_FIELDS:
        if field in existing and field in incoming and existing[field] != incoming[field]:
            return "IDENTITY_IMMUTABLE"
    if existing.get("tenantId") and incoming.get("tenantId") and existing["tenantId"] != incoming["tenantId"]:
        return "IDENTITY_IMMUTABLE"
    if object_type == "Point":
        if existing.get("deviceGlobalId") and incoming.get("deviceGlobalId"):
            if existing["deviceGlobalId"] != incoming["deviceGlobalId"]:
                return "IDENTITY_IMMUTABLE"
    return None


def outcome_message(outcome: str) -> str:
    if outcome == "VERSION_CONFLICT":
        return CONFLICT_MESSAGES["VERSION_CONFLICT"]
    if outcome == "IDENTITY_IMMUTABLE":
        return "Canonical identity fields are immutable."
    if outcome == "SCOPE_CONFLICT":
        return CONFLICT_MESSAGES["TENANT_SCOPE_CONFLICT"]
    if outcome not in UPDATE_OUTCOMES:
        return "Validation failed."
    return outcome
