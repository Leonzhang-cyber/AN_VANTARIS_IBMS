"""Deterministic model builders for read-only frontend skeletons."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from source_system_registry.digest import sha256_digest

from .enums import CONTRACT_VERSION


def build_page_skeleton(*, page_key: str, title: str, page_type: str, route_key: str, route_path_candidate: str, source_api_endpoint_key: str, source_projection_type: str, component_skeleton_ids: Sequence[str], card_skeleton_ids: Sequence[str], queue_skeleton_ids: Sequence[str], implementation_state: str) -> dict[str, Any]:
    item = {
        "pageSkeletonId": sha256_digest({"pageKey": page_key, "contract": "PAGE_SKELETON"}),
        "pageKey": page_key,
        "title": title,
        "pageType": page_type,
        "routeKey": route_key,
        "routePathCandidate": route_path_candidate,
        "sourceApiEndpointKey": source_api_endpoint_key,
        "sourceProjectionType": source_projection_type,
        "componentSkeletonIds": sorted(component_skeleton_ids),
        "cardSkeletonIds": sorted(card_skeleton_ids),
        "queueSkeletonIds": sorted(queue_skeleton_ids),
        "staticOnly": True,
        "readOnly": True,
        "productionEnabled": False,
        "liveApiCallEnabled": False,
        "dataMutationEnabled": False,
        "implementationState": implementation_state,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_route_skeleton(*, route_key: str, path_candidate: str, page_key: str, implementation_state: str) -> dict[str, Any]:
    item = {
        "routeSkeletonId": sha256_digest({"routeKey": route_key, "contract": "ROUTE_SKELETON"}),
        "routeKey": route_key,
        "pathCandidate": path_candidate,
        "pageKey": page_key,
        "productionRouteEnabled": False,
        "implementationState": implementation_state,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_component_skeleton(*, component_key: str, component_type: str, page_key: str, data_binding_skeleton_ids: Sequence[str]) -> dict[str, Any]:
    item = {
        "componentSkeletonId": sha256_digest({"componentKey": component_key, "contract": "COMPONENT_SKELETON"}),
        "componentKey": component_key,
        "componentType": component_type,
        "pageKey": page_key,
        "dataBindingSkeletonIds": sorted(data_binding_skeleton_ids),
        "staticOnly": True,
        "readOnly": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_data_binding_skeleton(*, page_key: str, source_api_endpoint_key: str, source_projection_type: str, source_artifact_path: str) -> dict[str, Any]:
    item = {
        "dataBindingSkeletonId": sha256_digest({"pageKey": page_key, "contract": "DATA_BINDING_SKELETON"}),
        "pageKey": page_key,
        "sourceApiEndpointKey": source_api_endpoint_key,
        "sourceProjectionType": source_projection_type,
        "sourceArtifactPath": source_artifact_path,
        "liveApiCallEnabled": False,
        "mockDataAllowed": True,
        "projectionBindingRequired": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_card_skeleton(*, card_type: str, page_key: str, title: str, source_projection_type: str) -> dict[str, Any]:
    item = {
        "cardSkeletonId": sha256_digest({"pageKey": page_key, "cardType": card_type, "contract": "CARD_SKELETON"}),
        "cardType": card_type,
        "pageKey": page_key,
        "title": title,
        "sourceProjectionType": source_projection_type,
        "staticOnly": True,
        "readOnly": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_queue_skeleton(*, queue_key: str, page_key: str, source_projection_type: str, row_count_policy: str) -> dict[str, Any]:
    item = {
        "queueSkeletonId": sha256_digest({"queueKey": queue_key, "contract": "QUEUE_SKELETON"}),
        "queueKey": queue_key,
        "pageKey": page_key,
        "sourceProjectionType": source_projection_type,
        "rowCountPolicy": row_count_policy,
        "staticOnly": True,
        "readOnly": True,
    }
    item["deterministicDigest"] = sha256_digest(item)
    return item


def build_frontend_readiness_gate(*, gate_id: str, gate_name: str, status: str, severity: str, blocking: bool, reason_codes: Sequence[str]) -> dict[str, Any]:
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


def build_read_only_frontend_skeleton(
    *,
    frontend_skeleton_id: str,
    authority: str,
    profile_id: str,
    implementation_status: str,
    readiness_outcome: str,
    summary: Mapping[str, Any],
    page_skeletons: Sequence[Mapping[str, Any]],
    route_skeletons: Sequence[Mapping[str, Any]],
    component_skeletons: Sequence[Mapping[str, Any]],
    data_binding_skeletons: Sequence[Mapping[str, Any]],
    card_skeletons: Sequence[Mapping[str, Any]],
    queue_skeletons: Sequence[Mapping[str, Any]],
    frontend_readiness_gates: Sequence[Mapping[str, Any]],
    boundary_matrix: Sequence[Mapping[str, Any]],
    source_artifact_references: Sequence[Mapping[str, Any]],
    generated_at_policy: str = "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
) -> dict[str, Any]:
    skeleton = {
        "frontendSkeletonId": frontend_skeleton_id,
        "contractVersion": CONTRACT_VERSION,
        "authority": authority,
        "profileId": profile_id,
        "implementationStatus": implementation_status,
        "readinessOutcome": readiness_outcome,
        "summary": dict(summary),
        "pageSkeletons": list(page_skeletons),
        "routeSkeletons": list(route_skeletons),
        "componentSkeletons": list(component_skeletons),
        "dataBindingSkeletons": list(data_binding_skeletons),
        "cardSkeletons": list(card_skeletons),
        "queueSkeletons": list(queue_skeletons),
        "frontendReadinessGates": list(frontend_readiness_gates),
        "boundaryMatrix": list(boundary_matrix),
        "sourceArtifactReferences": list(source_artifact_references),
        "generatedAtPolicy": generated_at_policy,
    }
    skeleton["deterministicDigest"] = sha256_digest({k: v for k, v in skeleton.items() if k != "deterministicDigest"})
    return skeleton
