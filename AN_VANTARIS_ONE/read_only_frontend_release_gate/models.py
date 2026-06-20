"""Deterministic model builders for read-only frontend implementation release gates."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_stage_result(*, stage_id: str, stage_name: str, pass_marker: str, artifact_path: str, validator_name: str, status: str, summary: Mapping[str, Any]) -> dict[str, Any]:
    item = {"stageId": stage_id, "stageName": stage_name, "passMarker": pass_marker, "artifactPath": artifact_path, "validatorName": validator_name, "status": status, "summary": dict(summary)}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_page_coverage_entry(*, page_key: str, page_skeleton_present: bool, page_contract_present: bool, layout_contract_present: bool, route_skeleton_present: bool, route_production_disabled: bool, static_only: bool, read_only: bool, live_api_call_disabled: bool, data_mutation_disabled: bool) -> dict[str, Any]:
    status = "PASS" if all([page_skeleton_present, page_contract_present, layout_contract_present, route_skeleton_present, route_production_disabled, static_only, read_only, live_api_call_disabled, data_mutation_disabled]) else "FAIL"
    item = {
        "coverageId": sha256_digest({"pageKey": page_key, "coverage": "PAGE"}),
        "pageKey": page_key,
        "pageSkeletonPresent": bool(page_skeleton_present),
        "pageContractPresent": bool(page_contract_present),
        "layoutContractPresent": bool(layout_contract_present),
        "routeSkeletonPresent": bool(route_skeleton_present),
        "routeProductionDisabled": bool(route_production_disabled),
        "staticOnly": bool(static_only),
        "readOnly": bool(read_only),
        "liveApiCallDisabled": bool(live_api_call_disabled),
        "dataMutationDisabled": bool(data_mutation_disabled),
        "status": status,
        "blocking": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_component_coverage_entry(*, page_key: str, component_binding_count: int, ui_state_contract_count: int, interaction_contract_count: int, data_binding_present: bool, card_binding_present: bool, queue_binding_present: bool) -> dict[str, Any]:
    status = "PASS" if component_binding_count == 3 and ui_state_contract_count == 6 and interaction_contract_count == 8 and data_binding_present and card_binding_present and queue_binding_present else "FAIL"
    item = {
        "coverageId": sha256_digest({"pageKey": page_key, "coverage": "COMPONENT"}),
        "pageKey": page_key,
        "componentBindingCount": int(component_binding_count),
        "uiStateContractCount": int(ui_state_contract_count),
        "interactionContractCount": int(interaction_contract_count),
        "dataBindingPresent": bool(data_binding_present),
        "cardBindingPresent": bool(card_binding_present),
        "queueBindingPresent": bool(queue_binding_present),
        "status": status,
        "blocking": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_interaction_coverage_entry(*, page_key: str, interaction_types: set[str], mutation_allowed: bool) -> dict[str, Any]:
    item = {
        "coverageId": sha256_digest({"pageKey": page_key, "coverage": "INTERACTION"}),
        "pageKey": page_key,
        "filterSupported": "FILTER" in interaction_types,
        "facetSupported": "FACET" in interaction_types,
        "paginationSupported": "PAGINATION" in interaction_types,
        "sortSupported": "SORT" in interaction_types,
        "searchSupported": "SEARCH" in interaction_types,
        "viewDetailsSupported": "VIEW_DETAILS" in interaction_types,
        "exportDisabled": "EXPORT_DISABLED" in interaction_types,
        "approvalDisabled": "APPROVAL_DISABLED" in interaction_types,
        "mutationAllowed": bool(mutation_allowed),
        "blocking": True,
    }
    item["status"] = "PASS" if all(item[key] is True for key in ("filterSupported", "facetSupported", "paginationSupported", "sortSupported", "searchSupported", "viewDetailsSupported", "exportDisabled", "approvalDisabled")) and item["mutationAllowed"] is False else "FAIL"
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_implementation_boundary_entry(*, boundary_key: str, expected_value: Any, actual_value: Any, blocking: bool) -> dict[str, Any]:
    item = {"boundaryId": sha256_digest({"boundaryKey": boundary_key}), "boundaryKey": boundary_key, "expectedValue": expected_value, "actualValue": actual_value, "status": "PASS" if expected_value == actual_value else "FAIL", "blocking": bool(blocking)}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_release_gate_result(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
    item = {"gateId": gate_id, "gateName": gate_name, "status": status, "severity": severity, "blocking": bool(blocking), "reasonCodes": sorted(str(code) for code in reason_codes)}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_implementation_decision(*, decision_state: str, read_only_frontend_implementation_allowed: bool, production_frontend_allowed: bool, real_route_implementation_allowed: bool, menu_implementation_allowed: bool, live_api_call_allowed: bool, data_mutation_allowed: bool, browser_smoke_allowed: bool, database_write_allowed: bool, runtime_activation_allowed: bool, production_activation_allowed: bool, api_implementation_required: bool, push_allowed: bool, decision_reason: str) -> dict[str, Any]:
    item = {
        "decisionState": decision_state,
        "readOnlyFrontendImplementationAllowed": bool(read_only_frontend_implementation_allowed),
        "productionFrontendAllowed": bool(production_frontend_allowed),
        "realRouteImplementationAllowed": bool(real_route_implementation_allowed),
        "menuImplementationAllowed": bool(menu_implementation_allowed),
        "liveApiCallAllowed": bool(live_api_call_allowed),
        "dataMutationAllowed": bool(data_mutation_allowed),
        "browserSmokeAllowed": bool(browser_smoke_allowed),
        "databaseWriteAllowed": bool(database_write_allowed),
        "runtimeActivationAllowed": bool(runtime_activation_allowed),
        "productionActivationAllowed": bool(production_activation_allowed),
        "apiImplementationRequired": bool(api_implementation_required),
        "pushAllowed": bool(push_allowed),
        "decisionReason": decision_reason,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    item = {"artifactType": artifact_type, "path": path, "digest": digest}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_read_only_frontend_implementation_release_gate(*, release_gate_id: str, authority: str, profile_id: str, implementation_status: str, readiness_outcome: str, summary: Mapping[str, Any], stage_results: Sequence[Mapping[str, Any]], page_coverage_matrix: Sequence[Mapping[str, Any]], component_coverage_matrix: Sequence[Mapping[str, Any]], interaction_coverage_matrix: Sequence[Mapping[str, Any]], implementation_boundary_matrix: Sequence[Mapping[str, Any]], release_gate_results: Sequence[Mapping[str, Any]], dependency_gate_results: Sequence[Mapping[str, Any]], implementation_decision: Mapping[str, Any], artifact_references: Sequence[Mapping[str, Any]], generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP") -> dict[str, Any]:
    gate = {
        "releaseGateId": release_gate_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "stageResults": list(stage_results),
        "pageCoverageMatrix": list(page_coverage_matrix),
        "componentCoverageMatrix": list(component_coverage_matrix),
        "interactionCoverageMatrix": list(interaction_coverage_matrix),
        "implementationBoundaryMatrix": list(implementation_boundary_matrix),
        "releaseGateResults": list(release_gate_results),
        "dependencyGateResults": list(dependency_gate_results),
        "implementationDecision": dict(implementation_decision),
        "artifactReferences": list(artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    gate["deterministicDigest"] = sha256_digest({k: v for k, v in gate.items() if k != "deterministicDigest"})
    return gate
