"""Bounded application-scoped integration support for the audit pilot."""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Mapping, Optional

from flask import current_app, g, request

from src.common.models.response import Result
from .in_memory import InMemoryAuditProvider
from .models import AuditEmissionResult, AuditRecord
from .service import AuditService

PILOT_EXTENSION_KEY = "vantaris_governance_audit_pilot_service"
PILOT_RUNTIME_STATUS = "NON_PRODUCTION_IN_MEMORY_PROVIDER"


@dataclass(frozen=True)
class PilotAuditInput:
    event_class: str
    action: str
    actor_id: str
    tenant_id: str
    site_id: Optional[str]
    target_type: str
    target_id: str
    route_id: str
    permission: str
    package_id: str
    outcome: str
    request_id: str
    trace_id: str
    correlation_id: str
    previous_state_digest: Optional[str] = None
    resulting_state_digest: Optional[str] = None
    denial_code: Optional[str] = None
    reason_code: Optional[str] = None


def canonical_state_digest(value: Mapping[str, Any]) -> str:
    """Return a stable digest without retaining the raw state."""
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def install_pilot_audit_service(service: AuditService) -> None:
    """Inject an app-scoped service; tests receive isolated provider lifecycle."""
    current_app.extensions[PILOT_EXTENSION_KEY] = service


def get_pilot_audit_service() -> AuditService:
    """Resolve the app-scoped pilot service without a module-global provider."""
    service = current_app.extensions.get(PILOT_EXTENSION_KEY)
    if service is None:
        service = AuditService(InMemoryAuditProvider())
        current_app.extensions[PILOT_EXTENSION_KEY] = service
        current_app.logger.warning(
            "Governance audit pilot is using %s; audit records are not durable.",
            PILOT_RUNTIME_STATUS,
        )
    return service


def new_compatibility_identifier(kind: str) -> str:
    """Generate an explicit compatibility identifier outside serialization."""
    return f"{kind}-compat-{uuid.uuid4().hex}"


def emit_pilot_audit(value: PilotAuditInput) -> AuditEmissionResult:
    """Build and emit one canonical record through AuditService only."""
    record = AuditRecord(
        audit_id=new_compatibility_identifier("audit"),
        event_class=value.event_class,
        action=value.action,
        occurred_at=datetime.now(timezone.utc),
        actor_type="USER",
        actor_id=value.actor_id,
        service_identity_id=None,
        tenant_id=value.tenant_id,
        site_id=value.site_id,
        subject_type=value.target_type,
        subject_id=value.target_id,
        target_type=value.target_type,
        target_id=value.target_id,
        route_id=value.route_id,
        request_id=value.request_id,
        trace_id=value.trace_id,
        correlation_id=value.correlation_id,
        permission=value.permission,
        package_id=value.package_id,
        outcome=value.outcome,
        denial_code=value.denial_code,
        reason_code=value.reason_code,
        previous_state_digest=value.previous_state_digest,
        resulting_state_digest=value.resulting_state_digest,
        source_ip_class=None,
        user_agent_class=None,
        contract_version="1.0.0",
        metadata_classification="INTERNAL",
        evidence_reference_ids=(),
    )
    return get_pilot_audit_service().emit(record)


def audit_create_version_pilot(function):
    """Audit exactly POST /api/system/versions after a successful mutation."""
    @wraps(function)
    def wrapper(*args, **kwargs):
        response = function(*args, **kwargs)
        flask_response, status = response
        if status != 200:
            return response
        data = request.get_json(silent=True) or {}
        jwt_payload = getattr(g, "jwt_payload", {}) or {}
        audit_result = emit_pilot_audit(PilotAuditInput(
            event_class="CONFIGURATION_CHANGE",
            action="platform.version.create",
            actor_id=getattr(g, "current_did", None) or "ACTOR_CONTEXT_UNAVAILABLE",
            tenant_id=(
                jwt_payload.get("tenant_id")
                or jwt_payload.get("tenantId")
                or "TENANT_CONTEXT_UNAVAILABLE"
            ),
            site_id=None,
            target_type="OperationalContext",
            target_id=str(data.get("version_code") or "TARGET_CONTEXT_UNAVAILABLE"),
            route_id="ROUTE-POST-C39FFBE9F5DC",
            permission="context:update",
            package_id="PKG-UCORE",
            outcome="SUCCESS",
            request_id=request.headers.get("X-Request-ID") or new_compatibility_identifier("request"),
            trace_id=request.headers.get("X-Trace-ID") or new_compatibility_identifier("trace"),
            correlation_id=request.headers.get("X-Correlation-ID") or new_compatibility_identifier("correlation"),
            resulting_state_digest=canonical_state_digest({
                "version_code": data.get("version_code"),
                "version_name": data.get("version_name"),
                "description": data.get("description"),
                "icon": data.get("icon"),
                "sort_order": data.get("sort_order", 0),
                "is_active": data.get("is_active", True),
                "is_default": data.get("is_default", False),
            }),
            reason_code="ADMINISTRATIVE_CONFIGURATION_CREATE",
        ))
        if not audit_result.accepted:
            return Result.error(code=500, message="Audit emission failed")
        return flask_response, status

    return wrapper
