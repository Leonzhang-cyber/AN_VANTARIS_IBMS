"""Controlled enumerations for read-only UConsole projections."""
from __future__ import annotations

from enum import Enum


class ProjectionType(str, Enum):
    UCONSOLE_INTEGRATION_HEALTH = "UCONSOLE_INTEGRATION_HEALTH"
    UCONSOLE_REVIEW_QUEUE = "UCONSOLE_REVIEW_QUEUE"
    UCONSOLE_EVIDENCE_CONTRACT = "UCONSOLE_EVIDENCE_CONTRACT"
    UNKNOWN = "UNKNOWN"


class CardType(str, Enum):
    SOURCE_SYSTEM_SUMMARY = "SOURCE_SYSTEM_SUMMARY"
    HEALTH_SUMMARY = "HEALTH_SUMMARY"
    REVIEW_QUEUE_SUMMARY = "REVIEW_QUEUE_SUMMARY"
    EVIDENCE_CONTRACT_SUMMARY = "EVIDENCE_CONTRACT_SUMMARY"
    RUNTIME_STATUS_SUMMARY = "RUNTIME_STATUS_SUMMARY"


class ProjectionStatus(str, Enum):
    READY_FOR_READ_ONLY_CONSUMPTION = "READY_FOR_READ_ONLY_CONSUMPTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RUNTIME_PENDING = "RUNTIME_PENDING"
    NOT_READY = "NOT_READY"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


PROJECTION_VERSION = "v1"
GENERATED_AT_POLICY = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP"

FACET_KEYS = (
    "sourceSystemKey",
    "lifecycleState",
    "approvalState",
    "readinessState",
    "reviewState",
    "evidenceContractState",
    "runtimeObserved",
    "runtimeVerified",
    "decisionRequired",
)

FILTER_KEYS = FACET_KEYS
