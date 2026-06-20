"""Deterministic model builders for read-only frontend page contracts."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_layout_contract(*, page_key: str, layout_type: str, required_regions: Sequence[str], responsive_policy: str) -> dict[str, Any]:
    item = {
        "layoutContractId": sha256_digest({"pageKey": page_key, "contract": "LAYOUT"}),
        "pageKey": page_key,
        "layoutType": layout_type,
        "requiredRegions": list(required_regions),
        "responsivePolicy": responsive_policy,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_component_binding_contract(*, page_key: str, component_key: str, component_type: str, source_data_binding_key: str, source_api_endpoint_key: str) -> dict[str, Any]:
    item = {
        "componentBindingId": sha256_digest({"pageKey": page_key, "componentKey": component_key, "contract": "COMPONENT_BINDING"}),
        "pageKey": page_key,
        "componentKey": component_key,
        "componentType": component_type,
        "sourceDataBindingKey": source_data_binding_key,
        "sourceApiEndpointKey": source_api_endpoint_key,
        "readOnly": True,
        "liveApiCallEnabled": False,
        "dataMutationEnabled": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_ui_state_contract(*, page_key: str, state_type: str, message_policy: str) -> dict[str, Any]:
    item = {
        "uiStateContractId": sha256_digest({"pageKey": page_key, "stateType": state_type, "contract": "UI_STATE"}),
        "pageKey": page_key,
        "stateType": state_type,
        "required": True,
        "messagePolicy": message_policy,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_interaction_contract(*, page_key: str, interaction_type: str, supported: bool = True) -> dict[str, Any]:
    item = {
        "interactionContractId": sha256_digest({"pageKey": page_key, "interactionType": interaction_type, "contract": "INTERACTION"}),
        "pageKey": page_key,
        "interactionType": interaction_type,
        "readOnly": True,
        "mutationAllowed": False,
        "supported": bool(supported),
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_page_contract(*, page_key: str, title: str, page_type: str, route_key: str, route_path_candidate: str, source_api_endpoint_key: str, layout_contract_id: str, component_binding_ids: Sequence[str], ui_state_contract_ids: Sequence[str], interaction_contract_ids: Sequence[str]) -> dict[str, Any]:
    item = {
        "pageContractId": sha256_digest({"pageKey": page_key, "contract": "PAGE"}),
        "pageKey": page_key,
        "title": title,
        "pageType": page_type,
        "routeKey": route_key,
        "routePathCandidate": route_path_candidate,
        "sourceApiEndpointKey": source_api_endpoint_key,
        "layoutContractId": layout_contract_id,
        "componentBindingIds": sorted(component_binding_ids),
        "uiStateContractIds": sorted(ui_state_contract_ids),
        "interactionContractIds": sorted(interaction_contract_ids),
        "staticOnly": True,
        "readOnly": True,
        "productionEnabled": False,
        "liveApiCallEnabled": False,
        "dataMutationEnabled": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_local_smoke_case(*, page_key: str, route_path_candidate: str, expected_components: int) -> dict[str, Any]:
    item = {
        "smokeCaseId": sha256_digest({"pageKey": page_key, "contract": "LOCAL_SMOKE"}),
        "pageKey": page_key,
        "routePathCandidate": route_path_candidate,
        "expectedPageContract": True,
        "expectedLayout": True,
        "expectedComponents": int(expected_components),
        "expectedUiStates": 6,
        "expectedInteractions": 8,
        "expectedNoLiveApiCall": True,
        "expectedNoMutation": True,
        "expectedNoProductionRoute": True,
        "browserLaunchRequired": False,
        "networkCallRequired": False,
        "localhostCallRequired": False,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_smoke_gate_result(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
    item = {
        "gateId": gate_id,
        "gateName": gate_name,
        "status": status,
        "severity": severity,
        "blocking": bool(blocking),
        "reasonCodes": sorted(str(code) for code in reason_codes),
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_boundary_entry(*, boundary_key: str, expected_value: Any, actual_value: Any, blocking: bool) -> dict[str, Any]:
    item = {
        "boundaryKey": boundary_key,
        "expectedValue": expected_value,
        "actualValue": actual_value,
        "status": "PASS" if expected_value == actual_value else "FAIL",
        "blocking": bool(blocking),
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_artifact_reference(*, artifact_type: str, path: str, digest: str) -> dict[str, Any]:
    item = {"artifactType": artifact_type, "path": path, "digest": digest}
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_read_only_frontend_page_contract(
    *,
    page_contract_id: str,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    page_contracts: Sequence[Mapping[str, Any]],
    layout_contracts: Sequence[Mapping[str, Any]],
    component_binding_contracts: Sequence[Mapping[str, Any]],
    ui_state_contracts: Sequence[Mapping[str, Any]],
    interaction_contracts: Sequence[Mapping[str, Any]],
    local_smoke_cases: Sequence[Mapping[str, Any]],
    smoke_gate_results: Sequence[Mapping[str, Any]],
    boundary_matrix: Sequence[Mapping[str, Any]],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    contract = {
        "pageContractId": page_contract_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "pageContracts": list(page_contracts),
        "layoutContracts": list(layout_contracts),
        "componentBindingContracts": list(component_binding_contracts),
        "uiStateContracts": list(ui_state_contracts),
        "interactionContracts": list(interaction_contracts),
        "localSmokeCases": list(local_smoke_cases),
        "smokeGateResults": list(smoke_gate_results),
        "boundaryMatrix": list(boundary_matrix),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    contract["deterministicDigest"] = sha256_digest({k: v for k, v in contract.items() if k != "deterministicDigest"})
    return contract
