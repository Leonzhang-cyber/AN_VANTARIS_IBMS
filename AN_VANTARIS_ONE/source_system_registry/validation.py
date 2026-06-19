"""Validation rules for generic source-system registry entries."""
from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from .enums import (
    GENERIC_SYSTEM_CATEGORIES,
    RegistryApprovalState,
    RegistryLifecycleState,
    VerificationState,
)
from .errors import SourceSystemRegistryError

_KEY_PATTERN = re.compile(r"^[A-Z0-9_]{2,32}$")
_CUSTOMER_ID_PATTERN = re.compile(r"^(TE3|DA21|DA31|Z1|Z2)-", re.IGNORECASE)


def normalize_source_system_key(value: str) -> str:
    normalized = value.strip().upper().replace("-", "_")
    normalized = re.sub(r"[^A-Z0-9_]", "", normalized)
    return normalized


def validate_source_system_key(source_system_key: str) -> None:
    if not source_system_key or not source_system_key.strip():
        raise SourceSystemRegistryError("MISSING_SOURCE_SYSTEM_KEY", "sourceSystemKey is required")
    if _CUSTOMER_ID_PATTERN.search(source_system_key):
        raise SourceSystemRegistryError("CUSTOMER_DERIVED_KEY", "sourceSystemKey must not derive from customer asset IDs")
    if not _KEY_PATTERN.match(source_system_key):
        raise SourceSystemRegistryError("UNSTABLE_SOURCE_SYSTEM_KEY", "sourceSystemKey must be stable and normalized")


def validate_registry_entry(entry: Mapping[str, Any], *, explicit_approval: bool = False) -> None:
    source_system_key = str(entry.get("sourceSystemKey", ""))
    validate_source_system_key(source_system_key)

    registry_entry_id = str(entry.get("registryEntryId", ""))
    if not registry_entry_id:
        raise SourceSystemRegistryError("MISSING_REGISTRY_ENTRY_ID", "registryEntryId is required")

    lifecycle = str(entry.get("lifecycleState", ""))
    if lifecycle not in {item.value for item in RegistryLifecycleState}:
        raise SourceSystemRegistryError("INVALID_LIFECYCLE_STATE", f"invalid lifecycleState: {lifecycle}")
    if lifecycle == "ACTIVE":
        raise SourceSystemRegistryError("FORBIDDEN_ACTIVE_LIFECYCLE", "ACTIVE lifecycle is forbidden for candidates")

    approval = str(entry.get("approvalState", ""))
    if approval not in {item.value for item in RegistryApprovalState}:
        raise SourceSystemRegistryError("INVALID_APPROVAL_STATE", f"invalid approvalState: {approval}")
    if approval in {RegistryApprovalState.APPROVED.value, RegistryApprovalState.REJECTED.value} and not explicit_approval:
        raise SourceSystemRegistryError(
            "APPROVAL_WITHOUT_DECISION",
            "approved or rejected state requires explicit approval input",
        )

    category = str(entry.get("systemCategory", ""))
    if category and category not in GENERIC_SYSTEM_CATEGORIES:
        raise SourceSystemRegistryError("INVALID_SYSTEM_CATEGORY", f"invalid systemCategory: {category}")

    for capability in entry.get("declaredCapabilities", []):
        _validate_capability(capability, require_verification_evidence=False)

    for capability in entry.get("verifiedCapabilities", []):
        _validate_capability(capability, require_verification_evidence=True)


def _validate_capability(capability: Mapping[str, Any], *, require_verification_evidence: bool) -> None:
    verification = str(capability.get("verificationState", VerificationState.NOT_VERIFIED.value))
    evidence = list(capability.get("evidenceReferences", []))
    if verification in {VerificationState.VERIFIED.value, VerificationState.EVIDENCE_SUPPORTED.value}:
        if not evidence:
            raise SourceSystemRegistryError(
                "VERIFIED_CAPABILITY_WITHOUT_EVIDENCE",
                "verified capabilities require evidence references",
            )
    if require_verification_evidence and verification == VerificationState.VERIFIED.value and not evidence:
        raise SourceSystemRegistryError(
            "VERIFIED_CAPABILITY_WITHOUT_EVIDENCE",
            "verified capabilities require evidence references",
        )


def validate_evidence_bundle(*, bindings: Sequence[Mapping[str, Any]], alias_package: Sequence[Mapping[str, Any]]) -> None:
    if not bindings:
        raise SourceSystemRegistryError("EMPTY_EVIDENCE", "classification bindings evidence is empty")
    for binding in bindings:
        if not binding.get("genericSystemCategory"):
            raise SourceSystemRegistryError("MALFORMED_EVIDENCE", "binding missing genericSystemCategory")
    for proposal in alias_package:
        if not proposal.get("proposalType"):
            raise SourceSystemRegistryError("MALFORMED_ALIAS_EVIDENCE", "alias proposal missing proposalType")
