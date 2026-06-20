"""Controlled states for UFMS FaultCase candidate projections."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "ufms-faultcase-candidate-projection.v1"


class FaultCaseEligibilityState(str, Enum):
    ELIGIBLE_FOR_REVIEW = "ELIGIBLE_FOR_REVIEW"
    BLOCKED_BY_RESOLUTION = "BLOCKED_BY_RESOLUTION"
    BLOCKED_BY_SOURCE_SYSTEM_REVIEW = "BLOCKED_BY_SOURCE_SYSTEM_REVIEW"
    BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class ProposedFaultCaseType(str, Enum):
    SECURITY_FAULT = "SECURITY_FAULT"
    COMMUNICATION_FAULT = "COMMUNICATION_FAULT"
    EQUIPMENT_FAULT = "EQUIPMENT_FAULT"
    INTEGRATION_FAULT = "INTEGRATION_FAULT"
    UNKNOWN = "UNKNOWN"


class ProposedFaultPriority(str, Enum):
    P1_CRITICAL = "P1_CRITICAL"
    P2_HIGH = "P2_HIGH"
    P3_MEDIUM = "P3_MEDIUM"
    P4_LOW = "P4_LOW"
    UNKNOWN = "UNKNOWN"


class ProposedFaultState(str, Enum):
    CANDIDATE = "CANDIDATE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"


class DownstreamCreationState(str, Enum):
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    NOT_CREATED = "NOT_CREATED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
