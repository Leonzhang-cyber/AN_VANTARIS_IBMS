"""Audit preview helpers for operator review policy guards."""
from __future__ import annotations

from typing import Any, Mapping

from source_system_registry.digest import sha256_digest

from .enums import ActorPolicy, AuditEventType, AuditPreviewState
from .models import build_audit_preview


def build_read_only_audit_preview(decision: Mapping[str, Any], policy_digest: str) -> dict[str, Any]:
    return build_audit_preview(
        decision_item_id=str(decision["decisionItemId"]),
        audit_event_type=AuditEventType.POLICY_GUARD_PREVIEW.value,
        audit_scope=str(decision.get("decisionScope", "UNKNOWN")),
        actor_policy=ActorPolicy.OPERATOR_REQUIRED.value,
        before_state=str(decision.get("decisionState", "UNKNOWN")),
        proposed_after_state=str(decision.get("decisionState", "UNKNOWN")),
        write_target="READ_ONLY_PREVIEW",
        write_allowed=False,
        approval_write_allowed=False,
        evidence_digest=sha256_digest(decision),
        policy_digest=policy_digest,
        audit_preview_state=AuditPreviewState.GENERATED_READ_ONLY.value,
    )
