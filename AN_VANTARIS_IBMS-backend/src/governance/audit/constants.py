"""Frozen value definitions for the Governance Audit Provider foundation."""
from __future__ import annotations

from enum import Enum


class ActorType(str, Enum):
    USER = "USER"
    SERVICE_IDENTITY = "SERVICE_IDENTITY"
    SYSTEM = "SYSTEM"
    ANONYMOUS = "ANONYMOUS"


class AuditOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    DENIED = "DENIED"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"


class AuditFailurePolicy(str, Enum):
    FAIL_CLOSED = "FAIL_CLOSED"
    FAIL_OPERATION_WITH_AUDIT_ERROR = "FAIL_OPERATION_WITH_AUDIT_ERROR"
    QUEUE_DURABLY_THEN_CONTINUE = "QUEUE_DURABLY_THEN_CONTINUE"
    BEST_EFFORT_NON_SENSITIVE_READ = "BEST_EFFORT_NON_SENSITIVE_READ"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class MetadataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    REDACTED = "REDACTED"


# Values and tenant/site/failure rules mirror audit-contract.v1.json.
EVENT_CLASS_POLICIES = {
    "AUTHENTICATION": (False, False, AuditFailurePolicy.FAIL_CLOSED),
    "AUTHORIZATION_DECISION": (True, False, AuditFailurePolicy.FAIL_CLOSED),
    "SECURITY_ADMINISTRATION": (True, False, AuditFailurePolicy.FAIL_CLOSED),
    "PACKAGE_LIFECYCLE": (True, False, AuditFailurePolicy.FAIL_CLOSED),
    "ENTITLEMENT_LIFECYCLE": (True, False, AuditFailurePolicy.FAIL_CLOSED),
    "CONFIGURATION_CHANGE": (True, False, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "CANONICAL_OBJECT_CREATE": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "CANONICAL_OBJECT_UPDATE": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "CANONICAL_OBJECT_RETIRE": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "BUSINESS_STATE_TRANSITION": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "WORK_LIFECYCLE": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "MAINTENANCE_LIFECYCLE": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "FAULT_ACTION": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "EVIDENCE_ACTION": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "REPORT_EXECUTION": (True, False, AuditFailurePolicy.BEST_EFFORT_NON_SENSITIVE_READ),
    "EXPORT": (True, False, AuditFailurePolicy.FAIL_CLOSED),
    "CONTROL_OPERATION": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "INTEGRATION_OPERATION": (True, True, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "AI_REQUEST": (True, False, AuditFailurePolicy.BEST_EFFORT_NON_SENSITIVE_READ),
    "AI_REVIEW": (True, False, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "MODEL_LIFECYCLE": (True, False, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
    "SENSITIVE_READ": (True, False, AuditFailurePolicy.BEST_EFFORT_NON_SENSITIVE_READ),
    "SYSTEM_HEALTH_CONTROL": (True, False, AuditFailurePolicy.FAIL_OPERATION_WITH_AUDIT_ERROR),
}

MAX_RECORD_SERIALIZED_BYTES = 64 * 1024
MAX_IDENTIFIER_LENGTH = 512
MAX_QUERY_LIMIT = 100
DEFAULT_QUERY_LIMIT = 50
