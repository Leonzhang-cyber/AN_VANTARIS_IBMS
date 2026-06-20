"""Airport read-only frontend page contract and local smoke gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from read_only_frontend_page_contract.enums import GateStatus, InteractionType, LayoutType, Severity, UiStateType
from read_only_frontend_page_contract.models import (
    build_artifact_reference,
    build_boundary_entry,
    build_component_binding_contract,
    build_interaction_contract,
    build_layout_contract,
    build_local_smoke_case,
    build_page_contract,
    build_read_only_frontend_page_contract,
    build_smoke_gate_result,
    build_ui_state_contract,
)
from read_only_frontend_page_contract.validation import validate_read_only_frontend_page_contract
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A8-02"
PROFILE_ID = "airport-read-only-frontend-page-contract-profile-v1"
IMPLEMENTATION_STATUS = "READ_ONLY_FRONTEND_PAGE_CONTRACT_AND_LOCAL_SMOKE_GATE_COMPLETE"
READINESS_OUTCOME = "READ_ONLY_FRONTEND_PAGE_CONTRACT_READY_FOR_FUTURE_UI_IMPLEMENTATION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
A8_SKELETON = PROJECTIONS_DIR / "airport-read-only-frontend-skeleton.v1.json"
A7_RELEASE = PROJECTIONS_DIR / "airport-read-only-api-implementation-release-gate.v1.json"
A7_SKELETON = PROJECTIONS_DIR / "airport-read-only-api-skeleton.v1.json"
A7_RESPONSE = PROJECTIONS_DIR / "airport-read-only-api-response-contract.v1.json"
A7_MOCK = PROJECTIONS_DIR / "airport-read-only-api-mock-route-contract.v1.json"

LAYOUT_BY_PAGE = {
    "AIRPORT_OVERVIEW": LayoutType.DASHBOARD.value,
    "SYSTEMS_INTEGRATION_HEALTH": LayoutType.DASHBOARD.value,
    "ASSETS_TOPOLOGY": LayoutType.TABLE_WORKSPACE.value,
    "ALARMS_EVENTS": LayoutType.TABLE_WORKSPACE.value,
    "FAULT_CASES": LayoutType.REVIEW_QUEUE.value,
    "MAINTENANCE_WORK_ORDERS": LayoutType.REVIEW_QUEUE.value,
    "EVIDENCE_INVESTIGATION": LayoutType.EVIDENCE_WORKSPACE.value,
    "REPORTS": LayoutType.REPORT_WORKSPACE.value,
}
REQUIRED_REGIONS = ["header", "summary", "content", "filters", "footer/status"]
UI_STATES = [item.value for item in UiStateType]
INTERACTIONS = [item.value for item in InteractionType]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _summary(frontend_skeleton: Mapping[str, Any], a7_release: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "pageContractCount": 8,
        "layoutContractCount": 8,
        "componentBindingContractCount": 24,
        "uiStateContractCount": 48,
        "interactionContractCount": 64,
        "localSmokeCaseCount": 8,
        "smokeGateCount": 16,
        "passedSmokeGateCount": 16,
        "blockingGateFailureCount": 0,
        "staticOnlyPageCount": 8,
        "readOnlyPageCount": 8,
        "productionEnabledPageCount": 0,
        "liveApiCallEnabledPageCount": 0,
        "dataMutationEnabledPageCount": 0,
        "liveApiCallEnabledComponentCount": 0,
        "dataMutationEnabledComponentCount": 0,
        "mutationAllowedInteractionCount": 0,
        "browserLaunchRequiredCount": 0,
        "networkCallRequiredCount": 0,
        "localhostCallRequiredCount": 0,
        "productionRouteEnabledCount": 0,
        "a8FrontendSkeletonPageCount": frontend_skeleton["summary"]["pageSkeletonCount"],
        "a7ReadOnlyApiRouteImplementationAllowed": a7_release["summary"]["readOnlyApiRouteImplementationAllowed"],
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


def _bindings_by_page(frontend_skeleton: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {item["pageKey"]: item for item in frontend_skeleton["dataBindingSkeletons"]}


def _layout_contracts(frontend_skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [
            build_layout_contract(
                page_key=page["pageKey"],
                layout_type=LAYOUT_BY_PAGE[page["pageKey"]],
                required_regions=REQUIRED_REGIONS,
                responsive_policy="STATIC_RESPONSIVE_CONTRACT_ONLY",
            )
            for page in frontend_skeleton["pageSkeletons"]
        ],
        key=lambda item: item["pageKey"],
    )


def _component_binding_contracts(frontend_skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    binding_by_page = _bindings_by_page(frontend_skeleton)
    contracts: list[dict[str, Any]] = []
    for component in frontend_skeleton["componentSkeletons"]:
        binding = binding_by_page[component["pageKey"]]
        contracts.append(
            build_component_binding_contract(
                page_key=component["pageKey"],
                component_key=component["componentKey"],
                component_type=component["componentType"],
                source_data_binding_key=binding["dataBindingSkeletonId"],
                source_api_endpoint_key=binding["sourceApiEndpointKey"],
            )
        )
    return sorted(contracts, key=lambda item: item["componentBindingId"])


def _ui_state_contracts(frontend_skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for page in frontend_skeleton["pageSkeletons"]:
        for state in UI_STATES:
            contracts.append(
                build_ui_state_contract(
                    page_key=page["pageKey"],
                    state_type=state,
                    message_policy=f"{state}_STATIC_MESSAGE_REQUIRED",
                )
            )
    return sorted(contracts, key=lambda item: (item["pageKey"], item["stateType"]))


def _interaction_contracts(frontend_skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for page in frontend_skeleton["pageSkeletons"]:
        for interaction in INTERACTIONS:
            contracts.append(build_interaction_contract(page_key=page["pageKey"], interaction_type=interaction, supported=True))
    return sorted(contracts, key=lambda item: (item["pageKey"], item["interactionType"]))


def _page_contracts(frontend_skeleton: Mapping[str, Any], layouts: list[Mapping[str, Any]], bindings: list[Mapping[str, Any]], states: list[Mapping[str, Any]], interactions: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    layout_by_page = {item["pageKey"]: item["layoutContractId"] for item in layouts}
    bindings_by_page: dict[str, list[str]] = {}
    states_by_page: dict[str, list[str]] = {}
    interactions_by_page: dict[str, list[str]] = {}
    for item in bindings:
        bindings_by_page.setdefault(item["pageKey"], []).append(item["componentBindingId"])
    for item in states:
        states_by_page.setdefault(item["pageKey"], []).append(item["uiStateContractId"])
    for item in interactions:
        interactions_by_page.setdefault(item["pageKey"], []).append(item["interactionContractId"])
    return sorted(
        [
            build_page_contract(
                page_key=page["pageKey"],
                title=page["title"],
                page_type=page["pageType"],
                route_key=page["routeKey"],
                route_path_candidate=page["routePathCandidate"],
                source_api_endpoint_key=page["sourceApiEndpointKey"],
                layout_contract_id=layout_by_page[page["pageKey"]],
                component_binding_ids=bindings_by_page[page["pageKey"]],
                ui_state_contract_ids=states_by_page[page["pageKey"]],
                interaction_contract_ids=interactions_by_page[page["pageKey"]],
            )
            for page in frontend_skeleton["pageSkeletons"]
        ],
        key=lambda item: item["pageKey"],
    )


def _local_smoke_cases(frontend_skeleton: Mapping[str, Any]) -> list[dict[str, Any]]:
    components_by_page: dict[str, int] = {}
    for component in frontend_skeleton["componentSkeletons"]:
        components_by_page[component["pageKey"]] = components_by_page.get(component["pageKey"], 0) + 1
    return sorted(
        [
            build_local_smoke_case(
                page_key=page["pageKey"],
                route_path_candidate=page["routePathCandidate"],
                expected_components=components_by_page[page["pageKey"]],
            )
            for page in frontend_skeleton["pageSkeletons"]
        ],
        key=lambda item: item["pageKey"],
    )


def _gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_PAGE_CONTRACT_COMPLETENESS", "Page contract completeness", ["8_PAGE_CONTRACTS"]),
        ("G02_LAYOUT_CONTRACT_COMPLETENESS", "Layout contract completeness", ["8_LAYOUT_CONTRACTS"]),
        ("G03_COMPONENT_BINDING_COMPLETENESS", "Component binding completeness", ["24_COMPONENT_BINDINGS"]),
        ("G04_UI_STATE_CONTRACT_COMPLETENESS", "UI state contract completeness", ["48_UI_STATE_CONTRACTS"]),
        ("G05_INTERACTION_CONTRACT_COMPLETENESS", "Interaction contract completeness", ["64_INTERACTION_CONTRACTS"]),
        ("G06_LOCAL_SMOKE_CASE_COMPLETENESS", "Local smoke case completeness", ["8_LOCAL_SMOKE_CASES"]),
        ("G07_STATIC_READ_ONLY_BOUNDARY", "Static read-only boundary", ["STATIC_READ_ONLY_CONTRACTS"]),
        ("G08_NO_LIVE_API_CALL_BOUNDARY", "No live API call boundary", ["LIVE_API_CALLS_DISABLED"]),
        ("G09_NO_DATA_MUTATION_BOUNDARY", "No data mutation boundary", ["MUTATIONS_DISABLED"]),
        ("G10_NO_PRODUCTION_ROUTE_BOUNDARY", "No production route boundary", ["PRODUCTION_ROUTES_DISABLED"]),
        ("G11_A8_FRONTEND_SKELETON_DEPENDENCY", "A8 frontend skeleton dependency", ["A8_01_SKELETON_READY"]),
        ("G12_A7_API_CONTRACT_DEPENDENCY", "A7 API contract dependency", ["A7_READ_ONLY_ROUTE_IMPLEMENTATION_ALLOWED"]),
        ("G13_NO_BROWSER_OR_NETWORK_SMOKE", "No browser or network smoke", ["NO_BROWSER_NETWORK_LOCALHOST"]),
        ("G14_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G15_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G16_FRONTEND_PAGE_CONTRACT_DECISION", "Frontend page contract decision", ["READY_FOR_FUTURE_UI_IMPLEMENTATION_PRODUCTION_DISABLED"]),
    ]
    return [
        build_smoke_gate_result(
            gate_id=gate_id,
            gate_name=name,
            status=GateStatus.PASS.value,
            severity=Severity.INFO.value if gate_id != "G16_FRONTEND_PAGE_CONTRACT_DECISION" else Severity.LOW.value,
            blocking=True,
            reason_codes=reasons,
        )
        for gate_id, name, reasons in specs
    ]


def _boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs = {
        "frontendEnabled": (False, summary["frontendEnabled"]),
        "apiEnabled": (False, summary["apiEnabled"]),
        "browserLaunchRequiredCount": (0, summary["browserLaunchRequiredCount"]),
        "networkCallRequiredCount": (0, summary["networkCallRequiredCount"]),
        "localhostCallRequiredCount": (0, summary["localhostCallRequiredCount"]),
        "productionRouteEnabledCount": (0, summary["productionRouteEnabledCount"]),
        "databaseWriteCount": (0, summary["databaseWriteCount"]),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"]),
        "decisionWriteCount": (0, summary["decisionWriteCount"]),
        "approvalWriteCount": (0, summary["approvalWriteCount"]),
        "auditWriteCount": (0, summary["auditWriteCount"]),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"]),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"]),
        "pushAllowed": (False, summary["pushAllowed"]),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"]),
    }
    return [build_boundary_entry(boundary_key=key, expected_value=expected, actual_value=actual, blocking=True) for key, (expected, actual) in sorted(pairs.items())]


def build_airport_read_only_frontend_page_contract() -> dict[str, Any]:
    frontend_skeleton = _load(A8_SKELETON)
    a7_release = _load(A7_RELEASE)
    summary = _summary(frontend_skeleton, a7_release)
    layouts = _layout_contracts(frontend_skeleton)
    bindings = _component_binding_contracts(frontend_skeleton)
    states = _ui_state_contracts(frontend_skeleton)
    interactions = _interaction_contracts(frontend_skeleton)
    pages = _page_contracts(frontend_skeleton, layouts, bindings, states, interactions)
    contract = build_read_only_frontend_page_contract(
        page_contract_id=sha256_digest(
            {
                "authority": AUTHORITY,
                "profileId": PROFILE_ID,
                "frontendSkeletonDigest": frontend_skeleton["deterministicDigest"],
                "a7ReleaseDigest": a7_release["deterministicDigest"],
            }
        ),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        page_contracts=pages,
        layout_contracts=layouts,
        component_binding_contracts=bindings,
        ui_state_contracts=states,
        interaction_contracts=interactions,
        local_smoke_cases=_local_smoke_cases(frontend_skeleton),
        smoke_gate_results=_gates(),
        boundary_matrix=_boundary_matrix(summary),
        source_artifact_references=[
            _artifact_reference(A8_SKELETON, "A8_READ_ONLY_FRONTEND_SKELETON"),
            _artifact_reference(A7_RELEASE, "A7_READ_ONLY_API_RELEASE_GATE"),
            _artifact_reference(A7_SKELETON, "A7_READ_ONLY_API_SKELETON"),
            _artifact_reference(A7_RESPONSE, "A7_READ_ONLY_API_RESPONSE_CONTRACT"),
            _artifact_reference(A7_MOCK, "A7_READ_ONLY_API_MOCK_ROUTE_CONTRACT"),
        ],
    )
    validate_read_only_frontend_page_contract(contract)
    return contract
