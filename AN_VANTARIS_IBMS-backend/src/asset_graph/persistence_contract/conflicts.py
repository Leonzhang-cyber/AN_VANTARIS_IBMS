"""Explicit persistence conflict model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .constants import CONFLICT_CODES


@dataclass(frozen=True)
class ConflictResult:
    conflict_code: str
    object_type: str
    blocking: bool
    retryable: bool
    requires_manual_review: bool
    safe_message: str

    def __post_init__(self) -> None:
        if self.conflict_code not in CONFLICT_CODES:
            raise ValueError(f"unknown conflict code: {self.conflict_code}")

    def serialize(self) -> dict[str, Any]:
        return {
            "conflictCode": self.conflict_code,
            "objectType": self.object_type,
            "blocking": self.blocking,
            "retryable": self.retryable,
            "requiresManualReview": self.requires_manual_review,
            "safeMessage": self.safe_message,
        }


def conflict_result(
    *,
    conflict_code: str,
    object_type: str,
    blocking: bool = True,
    retryable: bool = False,
    requires_manual_review: bool = False,
    safe_message: str,
) -> ConflictResult:
    return ConflictResult(
        conflict_code=conflict_code,
        object_type=object_type,
        blocking=blocking,
        retryable=retryable,
        requires_manual_review=requires_manual_review,
        safe_message=safe_message,
    )


CONFLICT_MESSAGES = {
    "SOURCE_IDENTITY_CONFLICT": "Source identity already bound to a different canonical object.",
    "CANONICAL_IDENTITY_CONFLICT": "Canonical identity already exists with conflicting content.",
    "TENANT_SCOPE_CONFLICT": "Tenant scope does not match the approved migration scope.",
    "SITE_SCOPE_CONFLICT": "Site scope does not match the approved migration scope.",
    "POINT_PARENT_CONFLICT": "Point parent device reference is invalid or out of scope.",
    "TAG_NAMESPACE_CONFLICT": "Tag namespace violates deterministic bounded namespace rules.",
    "RELATIONSHIP_ENDPOINT_CONFLICT": "Relationship endpoint is missing or out of scope.",
    "RELATIONSHIP_DUPLICATE_CONFLICT": "Relationship pair already exists with conflicting identity.",
    "VERSION_CONFLICT": "Expected version does not match current canonical version.",
    "IDEMPOTENCY_CONFLICT": "Idempotency key reused with a different command digest.",
    "MAPPING_VERSION_CONFLICT": "Mapping version does not match approved execution contract.",
    "EVIDENCE_DIGEST_CONFLICT": "Evidence digest does not match approved execution inputs.",
    "READINESS_DIGEST_CONFLICT": "Readiness digest does not match approved execution inputs.",
    "EXECUTION_DIGEST_CONFLICT": "Execution digest does not match approved execution inputs.",
}
