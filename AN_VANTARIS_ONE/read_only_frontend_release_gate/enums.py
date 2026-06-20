"""Enums for read-only frontend implementation release gates."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "read-only-frontend-implementation-release-gate.v1"


class GateStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class DecisionState(str, Enum):
    READY_FOR_READ_ONLY_FRONTEND_IMPLEMENTATION = "READY_FOR_READ_ONLY_FRONTEND_IMPLEMENTATION"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
