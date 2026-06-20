"""Enums for Operations Console Handoff Gates."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "operations-console-handoff-gate.v1"


class HandoffState(str, Enum):
    READY_FOR_HANDOFF = "READY_FOR_HANDOFF"
    READY_FOR_READ_ONLY_CONSUMPTION = "READY_FOR_READ_ONLY_CONSUMPTION"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class ContractCandidateState(str, Enum):
    CANDIDATE_READY = "CANDIDATE_READY"
    READ_ONLY_ONLY = "READ_ONLY_ONLY"
    BLOCKED = "BLOCKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class GateStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
