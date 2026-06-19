"""Generic source-system registry domain model builders."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .digest import sha256_digest
from .enums import (
    DeclarationState,
    IntegrationDirection,
    RegistryApprovalState,
    RegistryLifecycleState,
    VerificationState,
)


def build_evidence_reference(
    *,
    evidence_type: str,
    evidence_id: str,
    source_profile: str,
    source_record_count: int,
    provenance: str,
    digest: str | None = None,
) -> dict[str, Any]:
    ref = {
        "evidenceType": evidence_type,
        "evidenceId": evidence_id,
        "sourceProfile": source_profile,
        "sourceRecordCount": source_record_count,
        "provenance": provenance,
    }
    if digest:
        ref["digest"] = digest
    ref["resultDigest"] = sha256_digest({k: v for k, v in ref.items() if k != "resultDigest"})
    return ref


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def build_integration_declaration(
    *,
    integration_method: str = "UNDECLARED",
    protocol_family: str = "UNDECLARED",
    connector_reference: str | None = None,
    edge_gateway_reference: str | None = None,
    link_route_reference: str | None = None,
    direction: IntegrationDirection | str = IntegrationDirection.UNDECLARED,
    declaration_state: DeclarationState | str = DeclarationState.DECLARED,
) -> dict[str, Any]:
    decl = {
        "integrationMethod": integration_method,
        "protocolFamily": protocol_family,
        "connectorReference": connector_reference,
        "edgeGatewayReference": edge_gateway_reference,
        "linkRouteReference": link_route_reference,
        "direction": _enum_value(direction),
        "declarationState": _enum_value(declaration_state),
    }
    decl["resultDigest"] = sha256_digest({k: v for k, v in decl.items() if k != "resultDigest"})
    return decl


def build_capability_declaration(
    *,
    capability_key: str,
    declaration_state: DeclarationState | str = DeclarationState.DECLARED,
    verification_state: VerificationState | str = VerificationState.NOT_VERIFIED,
    evidence_references: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    capability = {
        "capabilityKey": capability_key,
        "declarationState": _enum_value(declaration_state),
        "verificationState": _enum_value(verification_state),
        "evidenceReferences": list(evidence_references or ()),
    }
    capability["resultDigest"] = sha256_digest({k: v for k, v in capability.items() if k != "resultDigest"})
    return capability


def build_health_policy_declaration(
    *,
    policy_key: str = "DEFAULT_EVIDENCE_ONLY",
    expected_signal_types: Sequence[str] | None = None,
    evaluation_mode: str = "DECLARATION_ONLY",
    stale_threshold_declaration: str | None = None,
    policy_state: DeclarationState | str = DeclarationState.DECLARED,
) -> dict[str, Any]:
    policy = {
        "policyKey": policy_key,
        "expectedSignalTypes": sorted(expected_signal_types or ()),
        "evaluationMode": evaluation_mode,
        "staleThresholdDeclaration": stale_threshold_declaration,
        "policyState": _enum_value(policy_state),
    }
    policy["resultDigest"] = sha256_digest({k: v for k, v in policy.items() if k != "resultDigest"})
    return policy


def build_registry_entry_id(*, source_system_key: str, created_from_profile: str, mapping_version: str) -> str:
    return sha256_digest(
        {
            "sourceSystemKey": source_system_key,
            "createdFromProfile": created_from_profile,
            "mappingVersion": mapping_version,
        }
    )
