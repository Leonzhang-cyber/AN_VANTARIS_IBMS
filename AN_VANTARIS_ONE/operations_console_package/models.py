"""Deterministic model builders for read-only Operations Console Packages."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_page_definition(
    *,
    page_id: str,
    page_key: str,
    title: str,
    description: str,
    page_type: str,
    readiness_state: str,
    source_projection_keys: Sequence[str],
    primary_card_ids: Sequence[str],
    queue_ids: Sequence[str],
    data_source_ids: Sequence[str],
    decision_required: bool,
    blocked: bool,
) -> dict[str, Any]:
    page = {
        "pageId": page_id,
        "pageKey": page_key,
        "title": title,
        "description": description,
        "pageType": page_type,
        "readinessState": readiness_state,
        "sourceProjectionKeys": sorted(str(key) for key in source_projection_keys),
        "primaryCardIds": sorted(str(card_id) for card_id in primary_card_ids),
        "queueIds": sorted(str(queue_id) for queue_id in queue_ids),
        "dataSourceIds": sorted(str(data_source_id) for data_source_id in data_source_ids),
        "decisionRequired": bool(decision_required),
        "blocked": bool(blocked),
    }
    page["deterministicDigest"] = sha256_digest(page)
    return page


def build_navigation_group(*, navigation_group_id: str, group_key: str, title: str, page_ids: Sequence[str], readiness_state: str) -> dict[str, Any]:
    group = {
        "navigationGroupId": navigation_group_id,
        "groupKey": group_key,
        "title": title,
        "pageIds": list(page_ids),
        "readinessState": readiness_state,
    }
    group["deterministicDigest"] = sha256_digest(group)
    return group


def build_console_card(
    *,
    card_id: str,
    card_type: str,
    title: str,
    severity: str,
    status: str,
    value: int | str | bool,
    unit: str,
    page_key: str,
    affected_source_system_keys: Sequence[str],
    affected_record_count: int,
    affected_device_evidence_count: int,
    decision_required: bool,
) -> dict[str, Any]:
    card = {
        "cardId": card_id,
        "cardType": card_type,
        "title": title,
        "severity": severity,
        "status": status,
        "value": value,
        "unit": unit,
        "pageKey": page_key,
        "affectedSourceSystemKeys": sorted(str(key) for key in affected_source_system_keys),
        "affectedRecordCount": int(affected_record_count),
        "affectedDeviceEvidenceCount": int(affected_device_evidence_count),
        "decisionRequired": bool(decision_required),
    }
    card["deterministicDigest"] = sha256_digest(card)
    return card


def build_package_data_source(*, data_source_id: str, data_source_key: str, source_artifact_path: str, source_projection_type: str) -> dict[str, Any]:
    data_source = {
        "dataSourceId": data_source_id,
        "dataSourceKey": data_source_key,
        "sourceArtifactPath": source_artifact_path,
        "sourceProjectionType": source_projection_type,
        "readOnly": True,
        "apiEnabled": False,
        "frontendEnabled": False,
        "databaseAccessEnabled": False,
    }
    data_source["deterministicDigest"] = sha256_digest(data_source)
    return data_source


def build_package_readiness_gate(
    *,
    gate_id: str,
    gate_name: str,
    status: str,
    severity: str,
    blocking: bool,
    reason_codes: Sequence[str],
    evidence_references: Sequence[str],
) -> dict[str, Any]:
    gate = {
        "gateId": gate_id,
        "gateName": gate_name,
        "status": status,
        "severity": severity,
        "blocking": bool(blocking),
        "reasonCodes": sorted(str(code) for code in reason_codes),
        "evidenceReferences": sorted(str(ref) for ref in evidence_references),
    }
    gate["deterministicDigest"] = sha256_digest(gate)
    return gate


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    ref = {"artifactType": artifact_type, "path": path, "digest": digest}
    ref["deterministicDigest"] = sha256_digest(ref)
    return ref


def build_operations_console_package(
    *,
    package_id: str,
    authority: str,
    profile_id: str,
    package_version: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    page_definitions: Sequence[Mapping[str, Any]],
    navigation_groups: Sequence[Mapping[str, Any]],
    console_cards: Sequence[Mapping[str, Any]],
    package_data_sources: Sequence[Mapping[str, Any]],
    package_readiness_gates: Sequence[Mapping[str, Any]],
    filters: Sequence[Mapping[str, Any]],
    facets: Sequence[Mapping[str, Any]],
    default_page: Mapping[str, Any],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    package = {
        "packageId": package_id,
        "authority": authority,
        "profileId": profile_id,
        "packageVersion": package_version,
        "contractVersion": CONTRACT_VERSION,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "pageDefinitions": list(page_definitions),
        "navigationGroups": list(navigation_groups),
        "consoleCards": list(console_cards),
        "packageDataSources": list(package_data_sources),
        "packageReadinessGates": list(package_readiness_gates),
        "filters": list(filters),
        "facets": list(facets),
        "defaultPage": dict(default_page),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    package["deterministicDigest"] = sha256_digest({k: v for k, v in package.items() if k != "deterministicDigest"})
    return package
