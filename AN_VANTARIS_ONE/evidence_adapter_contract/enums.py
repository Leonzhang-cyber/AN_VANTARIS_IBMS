"""Controlled enumerations for the Evidence Adapter Contract."""
from __future__ import annotations

from enum import Enum


class ProducerType(str, Enum):
    EDGE_GATEWAY = "EDGE_GATEWAY"
    LINK_ROUTE = "LINK_ROUTE"
    CONNECTOR_RUNTIME = "CONNECTOR_RUNTIME"
    MANUAL_IMPORT = "MANUAL_IMPORT"
    OFFLINE_FIXTURE = "OFFLINE_FIXTURE"
    UNKNOWN = "UNKNOWN"


class EvidenceKind(str, Enum):
    HEARTBEAT = "HEARTBEAT"
    CONNECTOR_STATUS = "CONNECTOR_STATUS"
    LINK_DELIVERY_ACK = "LINK_DELIVERY_ACK"
    ROUTE_STATUS = "ROUTE_STATUS"
    MAPPING_VERSION = "MAPPING_VERSION"
    SCHEMA_VERSION = "SCHEMA_VERSION"
    CAPABILITY_OBSERVATION = "CAPABILITY_OBSERVATION"
    HEALTH_SIGNAL = "HEALTH_SIGNAL"
    DELIVERY_EVIDENCE = "DELIVERY_EVIDENCE"
    CONFIG_DECLARATION = "CONFIG_DECLARATION"
    UNKNOWN = "UNKNOWN"


class EvidenceScope(str, Enum):
    SOURCE_SYSTEM = "SOURCE_SYSTEM"
    CONNECTOR = "CONNECTOR"
    EDGE_GATEWAY = "EDGE_GATEWAY"
    LINK_ROUTE = "LINK_ROUTE"
    CAPABILITY = "CAPABILITY"
    DELIVERY = "DELIVERY"
    UNKNOWN = "UNKNOWN"


class ValidationState(str, Enum):
    ACCEPTED_AS_EVIDENCE = "ACCEPTED_AS_EVIDENCE"
    REJECTED = "REJECTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNSUPPORTED = "UNSUPPORTED"
    NOT_RUNTIME_EVIDENCE = "NOT_RUNTIME_EVIDENCE"


class ContractReadiness(str, Enum):
    CONTRACT_DEFINED = "CONTRACT_DEFINED"
    FIXTURE_VALIDATED = "FIXTURE_VALIDATED"
    RUNTIME_ADAPTER_PENDING = "RUNTIME_ADAPTER_PENDING"


RUNTIME_PRODUCER_TYPES = frozenset(
    {
        ProducerType.EDGE_GATEWAY.value,
        ProducerType.LINK_ROUTE.value,
        ProducerType.CONNECTOR_RUNTIME.value,
    }
)

RUNTIME_EVIDENCE_KINDS = frozenset(
    {
        EvidenceKind.HEARTBEAT.value,
        EvidenceKind.CONNECTOR_STATUS.value,
        EvidenceKind.LINK_DELIVERY_ACK.value,
        EvidenceKind.ROUTE_STATUS.value,
        EvidenceKind.HEALTH_SIGNAL.value,
    }
)

FIXTURE_EVIDENCE_KINDS = frozenset(
    {
        EvidenceKind.CONFIG_DECLARATION.value,
        EvidenceKind.MAPPING_VERSION.value,
        EvidenceKind.SCHEMA_VERSION.value,
        EvidenceKind.CAPABILITY_OBSERVATION.value,
        EvidenceKind.DELIVERY_EVIDENCE.value,
    }
)

CONTRACT_VERSION = "v1"
