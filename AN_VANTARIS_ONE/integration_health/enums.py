"""Controlled enumerations for the generic Integration Health read model."""
from enum import Enum


class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class ReadinessState(str, Enum):
    NOT_READY = "NOT_READY"
    DECLARATION_READY = "DECLARATION_READY"
    EVIDENCE_READY = "EVIDENCE_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RUNTIME_VERIFICATION_REQUIRED = "RUNTIME_VERIFICATION_REQUIRED"
    VERIFIED_READY = "VERIFIED_READY"


class FindingSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
