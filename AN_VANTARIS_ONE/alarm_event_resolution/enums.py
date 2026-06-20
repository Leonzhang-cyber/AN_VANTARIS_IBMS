"""Controlled states for alarm/event resolution review projections."""
from __future__ import annotations

from enum import Enum

CONTRACT_VERSION = "alarm-event-asset-resolution-review.v1"


class ResolutionState(str, Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ResolutionConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class ReviewState(str, Enum):
    REGISTRY_APPROVAL_PENDING = "REGISTRY_APPROVAL_PENDING"
    ALIAS_APPROVAL_PENDING = "ALIAS_APPROVAL_PENDING"
    NAMESPACE_INTERPRETATION_PENDING = "NAMESPACE_INTERPRETATION_PENDING"
    RESOLUTION_REVIEW_REQUIRED = "RESOLUTION_REVIEW_REQUIRED"
    DOWNSTREAM_BLOCKED = "DOWNSTREAM_BLOCKED"
    NONE = "NONE"


class DownstreamCreationState(str, Enum):
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    NOT_CREATED = "NOT_CREATED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
