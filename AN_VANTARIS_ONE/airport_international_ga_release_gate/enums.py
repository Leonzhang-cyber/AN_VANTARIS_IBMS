"""Enums for Airport International GA release gates."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "airport-international-ga-release-gate.v1"


class GateStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ReleaseDecisionState(str, Enum):
    INTERNATIONAL_GA_READINESS_PASS = "INTERNATIONAL_GA_READINESS_PASS"
    INTERNATIONAL_GA_READINESS_PASS_WITH_WARNINGS = "INTERNATIONAL_GA_READINESS_PASS_WITH_WARNINGS"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class ReadinessState(str, Enum):
    COMPLETE = "COMPLETE"
    READY_FOR_READ_ONLY_CONSUMPTION = "READY_FOR_READ_ONLY_CONSUMPTION"
    READY_FOR_FUTURE_IMPLEMENTATION = "READY_FOR_FUTURE_IMPLEMENTATION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
