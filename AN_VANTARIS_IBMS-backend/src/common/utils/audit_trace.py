"""Lightweight audit trace helper for sensitive API boundaries (SECURITY-A9)."""
import logging
import uuid
from typing import Optional

from flask import g, request

logger = logging.getLogger(__name__)

TRACE_HEADER = "X-Trace-Id"


def get_or_create_trace_id() -> str:
    header = request.headers.get(TRACE_HEADER)
    if header is not None and str(header).strip():
        return str(header).strip()
    return str(uuid.uuid4())


def log_sensitive_api(
    action: str,
    *,
    device_code: Optional[str] = None,
    device_did: Optional[str] = None,
    category: Optional[str] = None,
    authenticated: Optional[bool] = None,
) -> str:
    """
    Log a safe audit summary for sensitive handlers.
    Does not log tokens, passwords, private keys, or full request bodies.
    """
    trace_id = get_or_create_trace_id()
    g.audit_trace_id = trace_id

    if authenticated is None:
        authenticated = bool(getattr(g, "current_did", None) or getattr(g, "jwt_payload", None))

    parts = [
        f"traceId={trace_id}",
        f"action={action}",
        f"method={request.method}",
        f"path={request.path}",
    ]
    if category:
        parts.append(f"category={category}")
    if device_code:
        parts.append(f"device_code={device_code}")
    if device_did:
        parts.append(f"device_did={device_did}")
    parts.append(f"authenticated={authenticated}")

    logger.info("[AUDIT] %s", " ".join(parts))
    return trace_id
