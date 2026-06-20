"""Validation helpers for read-only frontend skeletons."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import ReadOnlyFrontendSkeletonError


EXPECTED_SUMMARY = {
    "pageSkeletonCount": 8,
    "routeSkeletonCount": 8,
    "componentSkeletonCount": 24,
    "dataBindingSkeletonCount": 8,
    "cardSkeletonCount": 8,
    "queueSkeletonCount": 8,
    "frontendReadinessGateCount": 15,
    "passedGateCount": 15,
    "blockingGateFailureCount": 0,
    "staticOnlyPageCount": 8,
    "readOnlyPageCount": 8,
    "productionEnabledPageCount": 0,
    "liveApiCallEnabledPageCount": 0,
    "dataMutationEnabledPageCount": 0,
    "productionRouteEnabledCount": 0,
    "liveApiCallEnabledBindingCount": 0,
    "mockDataAllowedBindingCount": 8,
    "projectionBindingRequiredCount": 8,
    "a7ReadOnlyApiRouteImplementationAllowed": True,
    "a6FrontendSkeletonPhaseAllowed": True,
    "frontendSkeletonPhaseAllowed": True,
    "productionFrontendAllowed": False,
    "frontendEnabled": False,
    "apiEnabled": False,
    "databaseWriteCount": 0,
    "canonicalWriteCount": 0,
    "decisionWriteCount": 0,
    "approvalWriteCount": 0,
    "auditWriteCount": 0,
    "runtimeActivationAllowed": False,
    "productionActivationAllowed": False,
    "pushAllowed": False,
    "containsCustomerAssetIdentifiers": False,
    "crossIndustry": True,
    "airportSpecific": False,
}


def validate_read_only_frontend_skeleton(skeleton: Mapping[str, Any]) -> None:
    summary = skeleton.get("summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            raise ReadOnlyFrontendSkeletonError("SUMMARY_INVALID", f"{key} must be {value}")
    if len(skeleton.get("pageSkeletons", [])) != 8:
        raise ReadOnlyFrontendSkeletonError("PAGE_COUNT_INVALID", "exactly 8 page skeletons are required")
    if len(skeleton.get("routeSkeletons", [])) != 8:
        raise ReadOnlyFrontendSkeletonError("ROUTE_COUNT_INVALID", "exactly 8 route skeletons are required")
    if len(skeleton.get("componentSkeletons", [])) != 24:
        raise ReadOnlyFrontendSkeletonError("COMPONENT_COUNT_INVALID", "exactly 24 component skeletons are required")
    for page in skeleton.get("pageSkeletons", []):
        for key in ("staticOnly", "readOnly"):
            if page.get(key) is not True:
                raise ReadOnlyFrontendSkeletonError("PAGE_BOUNDARY_INVALID", f"{key} must be true")
        for key in ("productionEnabled", "liveApiCallEnabled", "dataMutationEnabled"):
            if page.get(key) is not False:
                raise ReadOnlyFrontendSkeletonError("PAGE_BOUNDARY_INVALID", f"{key} must be false")
    if any(route.get("productionRouteEnabled") is not False for route in skeleton.get("routeSkeletons", [])):
        raise ReadOnlyFrontendSkeletonError("ROUTE_BOUNDARY_INVALID", "production routes must remain disabled")
    if any(binding.get("liveApiCallEnabled") is not False or binding.get("mockDataAllowed") is not True or binding.get("projectionBindingRequired") is not True for binding in skeleton.get("dataBindingSkeletons", [])):
        raise ReadOnlyFrontendSkeletonError("BINDING_BOUNDARY_INVALID", "bindings must be projection-bound mock/static contracts")
    if any(gate.get("status") != "PASS" for gate in skeleton.get("frontendReadinessGates", [])):
        raise ReadOnlyFrontendSkeletonError("GATE_STATUS_INVALID", "all readiness gates must pass")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = (
        "sql" + "alchemy",
        "fla" + "sk",
        "fast" + "api",
        "req" + "uests.",
        "url" + "lib",
        "soc" + "ket",
        "src." + "ufms",
        "src." + "umms",
        "rea" + "ct",
        "v" + "ue",
    )
    found = [token for token in forbidden if token in lowered]
    if found:
        raise ReadOnlyFrontendSkeletonError("BOUNDARY_VIOLATION", ", ".join(found))
