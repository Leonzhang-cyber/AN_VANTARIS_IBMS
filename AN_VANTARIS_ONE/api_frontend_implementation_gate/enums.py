"""Enums for API / Frontend implementation readiness gates."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "api-frontend-implementation-readiness-gate.v1"


class GateStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class DecisionState(str, Enum):
    READY_FOR_READ_ONLY_SKELETON_PLANNING = "READY_FOR_READ_ONLY_SKELETON_PLANNING"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class ReadinessState(str, Enum):
    READY_FOR_SKELETON_PLANNING = "READY_FOR_SKELETON_PLANNING"
    CONTRACT_ONLY = "CONTRACT_ONLY"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
