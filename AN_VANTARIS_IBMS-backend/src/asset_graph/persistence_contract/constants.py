"""Persistence contract constants."""
from __future__ import annotations

CONTRACT_AUTHORITY = "ONE-A5-P1-16O"
CONTRACT_VERSION = "1.0.0"
CONTRACT_NAME = "VANTARIS ONE Canonical Asset Graph Persistence Contract"
IMPLEMENTATION_STATUS = "CONTRACT_ONLY"
WRITE_CUTOVER_STATUS = "NOT_READY_FOR_WRITE_CUTOVER"

REQUIRED_COMMAND_AUTHORITY = "APPROVED_READ_MIGRATION_EXECUTION"
REAL_EVIDENCE_CLASSIFICATION = "REAL_SANITIZED_EVIDENCE"
READY_FOR_READ_MIGRATION = "READY_FOR_READ_MIGRATION_CANDIDATE"

AUTHORIZATION_DENIED = "DENIED"
AUTHORIZATION_WAITING_REAL_EVIDENCE = "WAITING_FOR_REAL_EVIDENCE"
AUTHORIZATION_WAITING_READINESS = "WAITING_FOR_READINESS"
AUTHORIZATION_WAITING_PERSISTENCE_APPROVAL = "WAITING_FOR_PERSISTENCE_APPROVAL"
AUTHORIZATION_APPROVED_VALIDATION = "APPROVED_FOR_CANONICAL_WRITE_VALIDATION"

FORBIDDEN_AUTHORIZATION_DECISIONS = frozenset(
    {
        "APPROVED_FOR_WRITE_CUTOVER",
        "DUAL_WRITE_ACTIVE",
        "PRODUCTION_CUTOVER_COMPLETE",
    }
)

CONFLICT_CODES = frozenset(
    {
        "SOURCE_IDENTITY_CONFLICT",
        "CANONICAL_IDENTITY_CONFLICT",
        "TENANT_SCOPE_CONFLICT",
        "SITE_SCOPE_CONFLICT",
        "POINT_PARENT_CONFLICT",
        "TAG_NAMESPACE_CONFLICT",
        "RELATIONSHIP_ENDPOINT_CONFLICT",
        "RELATIONSHIP_DUPLICATE_CONFLICT",
        "VERSION_CONFLICT",
        "IDEMPOTENCY_CONFLICT",
        "MAPPING_VERSION_CONFLICT",
        "EVIDENCE_DIGEST_CONFLICT",
        "READINESS_DIGEST_CONFLICT",
        "EXECUTION_DIGEST_CONFLICT",
    }
)

UPDATE_OUTCOMES = frozenset(
    {
        "UPDATED",
        "VERSION_CONFLICT",
        "NOT_FOUND",
        "IDENTITY_IMMUTABLE",
        "SCOPE_CONFLICT",
        "VALIDATION_FAILED",
    }
)

COMMAND_STATUSES = frozenset(
    {
        "ACCEPTED",
        "REJECTED",
        "IDEMPOTENT_REPLAY",
        "ALREADY_APPLIED",
        "ROLLED_BACK",
    }
)

TRANSACTION_STATUSES = frozenset(
    {
        "STAGED",
        "COMMITTED",
        "ROLLED_BACK",
        "FAILED",
    }
)

AUDIT_OBLIGATIONS = frozenset(
    {
        "authorizationEvaluated",
        "commandAccepted",
        "commandRejected",
        "transactionStarted",
        "transactionCommitted",
        "transactionRolledBack",
        "idempotentReplay",
        "versionConflict",
        "scopeConflict",
        "providerUnavailable",
    }
)

OBJECT_TYPES = frozenset({"Device", "Point", "Tag", "AssetRelationship"})

RESULT_NAME = "VANTARIS ONE Asset Graph Persistence Result"
RESULT_VERSION = "1.0.0"

DEFAULT_CONTRACT_RELATIVE = "AN_VANTARIS_ONE/registries/asset-graph-persistence-contract.v1.json"
