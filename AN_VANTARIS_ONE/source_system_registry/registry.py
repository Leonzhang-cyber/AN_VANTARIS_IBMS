"""Generic registry candidate construction."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .digest import sha256_digest
from .enums import (
    DeclarationState,
    RegistryApprovalState,
    RegistryLifecycleState,
    VerificationState,
)
from .models import (
    build_capability_declaration,
    build_evidence_reference,
    build_health_policy_declaration,
    build_integration_declaration,
    build_registry_entry_id,
)
from .validation import normalize_source_system_key, validate_registry_entry


def build_registry_candidate(
    *,
    source_system_key: str,
    display_name: str,
    system_category: str,
    created_from_profile: str,
    mapping_version: str,
    schema_version: str,
    evidence_references: Sequence[Mapping[str, Any]],
    declared_capabilities: Sequence[Mapping[str, Any]] | None = None,
    verified_capabilities: Sequence[Mapping[str, Any]] | None = None,
    integration_declarations: Sequence[Mapping[str, Any]] | None = None,
    health_policy: Mapping[str, Any] | None = None,
    vendor: str | None = None,
    product: str | None = None,
    product_version: str | None = None,
    description: str | None = None,
    approval_state: RegistryApprovalState | str = RegistryApprovalState.DRAFT,
    lifecycle_state: RegistryLifecycleState | str = RegistryLifecycleState.CANDIDATE,
    explicit_approval: bool = False,
) -> dict[str, Any]:
    normalized_key = normalize_source_system_key(source_system_key)
    normalized_name = normalize_source_system_key(display_name)

    lifecycle_value = lifecycle_state.value if isinstance(lifecycle_state, RegistryLifecycleState) else str(lifecycle_state)
    approval_value = approval_state.value if isinstance(approval_state, RegistryApprovalState) else str(approval_state)

    entry = {
        "registryEntryId": build_registry_entry_id(
            source_system_key=normalized_key,
            created_from_profile=created_from_profile,
            mapping_version=mapping_version,
        ),
        "sourceSystemKey": normalized_key,
        "displayName": display_name,
        "normalizedName": normalized_name,
        "vendor": vendor,
        "product": product,
        "productVersion": product_version,
        "systemCategory": system_category,
        "description": description or f"Source system candidate for {normalized_key}",
        "integrationDeclarations": list(integration_declarations or [build_integration_declaration()]),
        "declaredCapabilities": list(
            declared_capabilities
            or [
                build_capability_declaration(
                    capability_key="SOURCE_IDENTITY_EVIDENCE",
                    declaration_state=DeclarationState.DECLARED,
                    verification_state=VerificationState.NOT_VERIFIED,
                )
            ]
        ),
        "verifiedCapabilities": list(verified_capabilities or ()),
        "healthPolicy": health_policy
        or build_health_policy_declaration(
            policy_key="EVIDENCE_ONLY_NO_RUNTIME_HEALTH",
            evaluation_mode="DECLARATION_ONLY",
        ),
        "lifecycleState": lifecycle_value,
        "approvalState": approval_value,
        "evidenceReferences": list(evidence_references),
        "createdFromProfile": created_from_profile,
        "schemaVersion": schema_version,
        "mappingVersion": mapping_version,
    }
    validate_registry_entry(entry, explicit_approval=explicit_approval)
    entry["resultDigest"] = sha256_digest({k: v for k, v in entry.items() if k != "resultDigest"})
    return entry
