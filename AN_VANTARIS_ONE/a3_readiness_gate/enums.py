"""Enums for A3 readiness release gates."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "a3-readiness-release-gate.v1"


class GateStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ReleaseDecisionState(str, Enum):
    RELEASE_GATE_PASS = "RELEASE_GATE_PASS"
    RELEASE_GATE_PASS_WITH_WARNINGS = "RELEASE_GATE_PASS_WITH_WARNINGS"
    RELEASE_GATE_FAIL = "RELEASE_GATE_FAIL"
    NOT_READY = "NOT_READY"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
