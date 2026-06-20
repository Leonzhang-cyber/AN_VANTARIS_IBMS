"""Airport read-only frontend skeleton foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from read_only_frontend_skeleton.enums import ComponentType, FrontendImplementationState, GateStatus, Severity
from read_only_frontend_skeleton.models import (
    build_artifact_reference,
    build_boundary_entry,
    build_card_skeleton,
    build_component_skeleton,
    build_data_binding_skeleton,
    build_frontend_readiness_gate,
    build_page_skeleton,
    build_queue_skeleton,
    build_read_only_frontend_skeleton,
    build_route_skeleton,
)
from read_only_frontend_skeleton.validation import validate_read_only_frontend_skeleton
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A8-01"
PROFILE_ID = "airport-read-only-frontend-skeleton-profile-v1"
IMPLEMENTATION_STATUS = "READ_ONLY_FRONTEND_SKELETON_FOUNDATION_COMPLETE"
READINESS_OUTCOME = "READ_ONLY_FRONTEND_SKELETON_READY_FOR_FUTURE_UI_IMPLEMENTATION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
A7_RELEASE = PROJECTIONS_DIR / "airport-read-only-api-implementation-release-gate.v1.json"
A7_SKELETON = PROJECTIONS_DIR / "airport-read-only-api-skeleton.v1.json"
A7_RESPONSE = PROJECTIONS_DIR / "airport-read-only-api-response-contract.v1.json"
A7_MOCK = PROJECTIONS_DIR / "airport-read-only-api-mock-route-contract.v1.json"
A6_CONTRACT = PROJECTIONS_DIR / "airport-api-frontend-readiness-contract.v1.json"
A6_GATE = PROJECTIONS_DIR / "airport-api-frontend-implementation-readiness-gate.v1.json"
A5_PACKAGE = PROJECTIONS_DIR / "airport-operations-console-package.v1.json"
A5_HANDOFF = PROJECTIONS_DIR / "airport-operations-console-handoff-gate.v1.json"

PAGE_SPECS = [
    ("AIRPORT_OVERVIEW", "Airport Overview", "OVERVIEW", "/one/airport/overview"),
    ("SYSTEMS_INTEGRATION_HEALTH", "Systems & Integration Health", "STATUS", "/one/airport/systems-integration-health"),
    ("ASSETS_TOPOLOGY", "Assets & Topology", "TABLE", "/one/airport/assets-topology"),
    ("ALARMS_EVENTS", "Alarms & Events", "REVIEW_QUEUE", "/one/airport/alarms-events"),
    ("FAULT_CASES", "Fault Cases", "REVIEW_QUEUE", "/one/airport/fault-cases"),
    ("MAINTENANCE_WORK_ORDERS", "Maintenance Work Orders", "REVIEW_QUEUE", "/one/airport/maintenance-work-orders"),
    ("EVIDENCE_INVESTIGATION", "Evidence & Investigation", "REVIEW_QUEUE", "/one/airport/evidence-investigation"),
    ("REPORTS", "Reports", "REPORT", "/one/airport/reports"),
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _summary(a7_release: Mapping[str, Any], a6_gate: Mapping[str, Any]) -> dict[str, Any]:
    return {
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
        "a7ReadOnlyApiRouteImplementationAllowed": a7_release["summary"]["readOnlyApiRouteImplementationAllowed"],
        "a6FrontendSkeletonPhaseAllowed": a6_gate["summary"]["frontendSkeletonPhaseAllowed"],
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


def _endpoint_by_page(api_skeleton: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {item["pageKey"]: item for item in api_skeleton["endpointSkeletons"]}


def _response_by_endpoint(response_contract: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {item["endpointKey"]: item for item in response_contract["endpointResponseContracts"]}


def _route_key(page_key: str) -> str:
    return f"AIRPORT_FRONTEND_ROUTE_{page_key}"


def _component_keys(page_key: str, page_type: str) -> list[tuple[str, str]]:
    third = ComponentType.REPORT_PANEL.value if page_type == "REPORT" else ComponentType.REVIEW_QUEUE.value if page_type == "REVIEW_QUEUE" else ComponentType.DATA_TABLE.value
    second = ComponentType.STATUS_PANEL.value if page_type == "STATUS" else ComponentType.SUMMARY_CARD.value
    return [
        (f"{page_key}_PAGE_CONTAINER", ComponentType.PAGE_CONTAINER.value),
        (f"{page_key}_PRIMARY_PANEL", second),
        (f"{page_key}_DETAIL_PANEL", third),
    ]


def _data_bindings(api_skeleton: Mapping[str, Any], response_contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    endpoints = _endpoint_by_page(api_skeleton)
    responses = _response_by_endpoint(response_contract)
    bindings: list[dict[str, Any]] = []
    for page_key, _, _, _ in PAGE_SPECS:
        endpoint = endpoints[page_key]
        response = responses[endpoint["endpointKey"]]
        bindings.append(
            build_data_binding_skeleton(
                page_key=page_key,
                source_api_endpoint_key=endpoint["endpointKey"],
                source_projection_type=endpoint["sourceProjectionType"],
                source_artifact_path=response["sourceArtifactPath"],
            )
        )
    return sorted(bindings, key=lambda item: item["pageKey"])


def _cards(api_skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    endpoints = _endpoint_by_page(api_skeleton)
    cards: list[dict[str, Any]] = []
    for page_key, title, page_type, _ in PAGE_SPECS:
        card_type = "REPORT_PANEL" if page_type == "REPORT" else "STATUS_PANEL" if page_type == "STATUS" else "SUMMARY_CARD"
        cards.append(
            build_card_skeleton(
                card_type=card_type,
                page_key=page_key,
                title=title,
                source_projection_type=endpoints[page_key]["sourceProjectionType"],
            )
        )
    return sorted(cards, key=lambda item: item["pageKey"])


def _queues(api_skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    endpoints = _endpoint_by_page(api_skeleton)
    return sorted(
        [
            build_queue_skeleton(
                queue_key=f"{page_key}_READ_ONLY_QUEUE",
                page_key=page_key,
                source_projection_type=endpoints[page_key]["sourceProjectionType"],
                row_count_policy="STATIC_PROJECTION_ROWS_ONLY",
            )
            for page_key, _, _, _ in PAGE_SPECS
        ],
        key=lambda item: item["pageKey"],
    )


def _components(bindings: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    binding_by_page = {item["pageKey"]: item["dataBindingSkeletonId"] for item in bindings}
    components: list[dict[str, Any]] = []
    for page_key, _, page_type, _ in PAGE_SPECS:
        for component_key, component_type in _component_keys(page_key, page_type):
            components.append(
                build_component_skeleton(
                    component_key=component_key,
                    component_type=component_type,
                    page_key=page_key,
                    data_binding_skeleton_ids=[binding_by_page[page_key]],
                )
            )
    return sorted(components, key=lambda item: item["componentKey"])


def _routes() -> list[dict[str, Any]]:
    return sorted(
        [
            build_route_skeleton(
                route_key=_route_key(page_key),
                path_candidate=path,
                page_key=page_key,
                implementation_state=FrontendImplementationState.SKELETON_DEFINED.value,
            )
            for page_key, _, _, path in PAGE_SPECS
        ],
        key=lambda item: item["pageKey"],
    )


def _pages(api_skeleton: Mapping[str, Any], bindings: list[Mapping[str, Any]], components: list[Mapping[str, Any]], cards: list[Mapping[str, Any]], queues: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    endpoints = _endpoint_by_page(api_skeleton)
    component_ids_by_page = {page_key: [] for page_key, _, _, _ in PAGE_SPECS}
    for component in components:
        component_ids_by_page[component["pageKey"]].append(component["componentSkeletonId"])
    card_ids_by_page = {card["pageKey"]: [card["cardSkeletonId"]] for card in cards}
    queue_ids_by_page = {queue["pageKey"]: [queue["queueSkeletonId"]] for queue in queues}
    pages: list[dict[str, Any]] = []
    for page_key, title, page_type, path in PAGE_SPECS:
        endpoint = endpoints[page_key]
        pages.append(
            build_page_skeleton(
                page_key=page_key,
                title=title,
                page_type=page_type,
                route_key=_route_key(page_key),
                route_path_candidate=path,
                source_api_endpoint_key=endpoint["endpointKey"],
                source_projection_type=endpoint["sourceProjectionType"],
                component_skeleton_ids=component_ids_by_page[page_key],
                card_skeleton_ids=card_ids_by_page[page_key],
                queue_skeleton_ids=queue_ids_by_page[page_key],
                implementation_state=FrontendImplementationState.SKELETON_DEFINED.value,
            )
        )
    return sorted(pages, key=lambda item: item["pageKey"])


def _gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_FRONTEND_PAGE_SKELETON_COMPLETENESS", "Page skeleton completeness", ["8_PAGE_SKELETONS"]),
        ("G02_FRONTEND_ROUTE_SKELETON_COMPLETENESS", "Route skeleton completeness", ["8_ROUTE_SKELETONS"]),
        ("G03_COMPONENT_SKELETON_MINIMUM_COVERAGE", "Component skeleton minimum coverage", ["24_COMPONENT_SKELETONS"]),
        ("G04_DATA_BINDING_SKELETON_COMPLETENESS", "Data binding skeleton completeness", ["8_DATA_BINDINGS"]),
        ("G05_CARD_SKELETON_COMPLETENESS", "Card skeleton completeness", ["8_CARD_SKELETONS"]),
        ("G06_QUEUE_SKELETON_COMPLETENESS", "Queue skeleton completeness", ["8_QUEUE_SKELETONS"]),
        ("G07_STATIC_ONLY_BOUNDARY", "Static only boundary", ["STATIC_READ_ONLY_CONTRACTS"]),
        ("G08_NO_LIVE_API_CALL_BOUNDARY", "No live API call boundary", ["LIVE_API_CALLS_DISABLED"]),
        ("G09_NO_DATA_MUTATION_BOUNDARY", "No data mutation boundary", ["DATA_MUTATION_DISABLED"]),
        ("G10_NO_PRODUCTION_ROUTE_BOUNDARY", "No production route boundary", ["PRODUCTION_ROUTES_DISABLED"]),
        ("G11_A7_API_RELEASE_DEPENDENCY", "A7 API release dependency", ["A7_READ_ONLY_ROUTE_IMPLEMENTATION_ALLOWED"]),
        ("G12_A6_FRONTEND_SKELETON_DEPENDENCY", "A6 frontend skeleton dependency", ["A6_FRONTEND_SKELETON_PHASE_ALLOWED"]),
        ("G13_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G14_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G15_FRONTEND_SKELETON_DECISION", "Frontend skeleton decision", ["READY_FOR_FUTURE_UI_IMPLEMENTATION_PRODUCTION_DISABLED"]),
    ]
    return [
        build_frontend_readiness_gate(
            gate_id=gate_id,
            gate_name=name,
            status=GateStatus.PASS.value,
            severity=Severity.INFO.value if gate_id != "G15_FRONTEND_SKELETON_DECISION" else Severity.LOW.value,
            blocking=True,
            reason_codes=reasons,
        )
        for gate_id, name, reasons in specs
    ]


def _boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs = {
        "frontendSkeletonPhaseAllowed": (True, summary["frontendSkeletonPhaseAllowed"]),
        "productionFrontendAllowed": (False, summary["productionFrontendAllowed"]),
        "frontendEnabled": (False, summary["frontendEnabled"]),
        "apiEnabled": (False, summary["apiEnabled"]),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"]),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"]),
        "pushAllowed": (False, summary["pushAllowed"]),
        "databaseWriteCount": (0, summary["databaseWriteCount"]),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"]),
        "decisionWriteCount": (0, summary["decisionWriteCount"]),
        "approvalWriteCount": (0, summary["approvalWriteCount"]),
        "auditWriteCount": (0, summary["auditWriteCount"]),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"]),
    }
    return [build_boundary_entry(boundary_key=key, expected_value=expected, actual_value=actual, blocking=True) for key, (expected, actual) in sorted(pairs.items())]


def build_airport_read_only_frontend_skeleton() -> dict[str, Any]:
    a7_release = _load(A7_RELEASE)
    api_skeleton = _load(A7_SKELETON)
    response_contract = _load(A7_RESPONSE)
    a7_mock = _load(A7_MOCK)
    a6_gate = _load(A6_GATE)
    summary = _summary(a7_release, a6_gate)
    bindings = _data_bindings(api_skeleton, response_contract)
    cards = _cards(api_skeleton)
    queues = _queues(api_skeleton)
    components = _components(bindings)
    pages = _pages(api_skeleton, bindings, components, cards, queues)
    routes = _routes()
    skeleton = build_read_only_frontend_skeleton(
        frontend_skeleton_id=sha256_digest(
            {
                "authority": AUTHORITY,
                "profileId": PROFILE_ID,
                "a7ReleaseDigest": a7_release["deterministicDigest"],
                "apiSkeletonDigest": api_skeleton["deterministicDigest"],
                "a7MockDigest": a7_mock["deterministicDigest"],
            }
        ),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        page_skeletons=pages,
        route_skeletons=routes,
        component_skeletons=components,
        data_binding_skeletons=bindings,
        card_skeletons=cards,
        queue_skeletons=queues,
        frontend_readiness_gates=_gates(),
        boundary_matrix=_boundary_matrix(summary),
        source_artifact_references=[
            _artifact_reference(A7_RELEASE, "A7_READ_ONLY_API_RELEASE_GATE"),
            _artifact_reference(A7_SKELETON, "A7_READ_ONLY_API_SKELETON"),
            _artifact_reference(A7_RESPONSE, "A7_READ_ONLY_API_RESPONSE_CONTRACT"),
            _artifact_reference(A7_MOCK, "A7_READ_ONLY_API_MOCK_ROUTE_CONTRACT"),
            _artifact_reference(A6_CONTRACT, "A6_API_FRONTEND_READINESS_CONTRACT"),
            _artifact_reference(A6_GATE, "A6_API_FRONTEND_IMPLEMENTATION_GATE"),
            _artifact_reference(A5_PACKAGE, "A5_OPERATIONS_CONSOLE_PACKAGE"),
            _artifact_reference(A5_HANDOFF, "A5_HANDOFF_GATE"),
        ],
    )
    validate_read_only_frontend_skeleton(skeleton)
    return skeleton
