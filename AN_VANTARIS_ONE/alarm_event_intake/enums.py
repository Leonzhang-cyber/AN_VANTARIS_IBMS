"""Controlled enums for canonical alarm/event intake candidates."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "canonical-alarm-event-intake.v1"


class EventKind(str, Enum):
    ALARM = "ALARM"
    EVENT = "EVENT"
    FAULT = "FAULT"
    STATUS_CHANGE = "STATUS_CHANGE"
    HEALTH_SIGNAL = "HEALTH_SIGNAL"
    MAINTENANCE_SIGNAL = "MAINTENANCE_SIGNAL"
    UNKNOWN = "UNKNOWN"


class EventCategory(str, Enum):
    SAFETY = "SAFETY"
    SECURITY = "SECURITY"
    FACILITY = "FACILITY"
    EQUIPMENT = "EQUIPMENT"
    NETWORK = "NETWORK"
    COMMUNICATION = "COMMUNICATION"
    POWER = "POWER"
    ENVIRONMENT = "ENVIRONMENT"
    MAINTENANCE = "MAINTENANCE"
    INTEGRATION = "INTEGRATION"
    UNKNOWN = "UNKNOWN"


class EventSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class EventState(str, Enum):
    RAISED = "RAISED"
    CLEARED = "CLEARED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    UPDATED = "UPDATED"
    UNKNOWN = "UNKNOWN"


class ValidationState(str, Enum):
    ACCEPTED_AS_CANDIDATE = "ACCEPTED_AS_CANDIDATE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REJECTED = "REJECTED"
    UNSUPPORTED = "UNSUPPORTED"


class NormalizationState(str, Enum):
    NORMALIZED = "NORMALIZED"
    PARTIAL = "PARTIAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REJECTED = "REJECTED"


class ResolutionState(str, Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class CandidateLifecycleState(str, Enum):
    CANDIDATE = "CANDIDATE"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"


class CandidateApprovalState(str, Enum):
    DRAFT = "DRAFT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DownstreamCandidateState(str, Enum):
    NOT_CREATED = "NOT_CREATED"
    ELIGIBLE = "ELIGIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
