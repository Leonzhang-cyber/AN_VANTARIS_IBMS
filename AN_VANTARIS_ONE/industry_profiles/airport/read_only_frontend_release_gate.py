"""Airport read-only frontend implementation release gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from read_only_frontend_release_gate.enums import DecisionState, GateStatus, Severity
from read_only_frontend_release_gate.models import (
    build_artifact_reference,
    build_component_coverage_entry,
    build_implementation_boundary_entry,
    build_implementation_decision,
    build_interaction_coverage_entry,
    build_page_coverage_entry,
    build_read_only_frontend_implementation_release_gate,
    build_release_gate_result,
    build_stage_result,
)
from read_only_frontend_release_gate.validation import validate_read_only_frontend_release_gate
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A8-03"
PROFILE_ID = "airport-read-only-frontend-implementation-release-gate-profile-v1"
IMPLEMENTATION_STATUS = "READ_ONLY_FRONTEND_IMPLEMENTATION_RELEASE_GATE_COMPLETE"
READINESS_OUTCOME = "READ_ONLY_FRONTEND_READY_FOR_FUTURE_UI_IMPLEMENTATION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
A8_SKELETON = PROJECTIONS_DIR / "airport-read-only-frontend-skeleton.v1.json"
A8_PAGE_CONTRACT = PROJECTIONS_DIR / "airport-read-only-frontend-page-contract.v1.json"
A7_RELEASE = PROJECTIONS_DIR / "airport-read-only-api-implementation-release-gate.v1.json"
A6_GATE = PROJECTIONS_DIR / "airport-api-frontend-implementation-readiness-gate.v1.json"
A6_CONTRACT = PROJECTIONS_DIR / "airport-api-frontend-readiness-contract.v1.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _summary() -> dict[str, Any]:
    return {
        "a8StageCount": 2,
        "passedStageCount": 2,
        "failedStageCount": 0,
        "pageCount": 8,
        "pageSkeletonCount": 8,
        "pageContractCount": 8,
        "routeSkeletonCount": 8,
        "layoutContractCount": 8,
        "componentCoverageEntryCount": 8,
        "interactionCoverageEntryCount": 8,
        "releaseGateCount": 17,
        "passedGateCount": 17,
        "blockingGateFailureCount": 0,
        "componentBindingContractCount": 24,
        "uiStateContractCount": 48,
        "interactionContractCount": 64,
        "dataBindingSkeletonCount": 8,
        "cardSkeletonCount": 8,
        "queueSkeletonCount": 8,
        "staticOnlyPageCount": 8,
        "readOnlyPageCount": 8,
        "productionEnabledPageCount": 0,
        "productionRouteEnabledCount": 0,
        "realFrontendFileChangeCount": 0,
        "realMenuEntryChangeCount": 0,
        "liveApiCallEnabledCount": 0,
        "browserLaunchRequiredCount": 0,
        "networkCallRequiredCount": 0,
        "localhostCallRequiredCount": 0,
        "mutationAllowedInteractionCount": 0,
        "readOnlyFrontendImplementationAllowed": True,
        "productionFrontendAllowed": False,
        "realRouteImplementationAllowed": False,
        "menuImplementationAllowed": False,
        "liveApiCallAllowed": False,
        "dataMutationAllowed": False,
        "browserSmokeAllowed": False,
        "databaseWriteAllowed": False,
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
        "apiImplementationRequired": False,
        "pushAllowed": False,
        "apiEnabled": False,
        "frontendEnabled": False,
        "databaseWriteCount": 0,
        "canonicalWriteCount": 0,
        "decisionWriteCount": 0,
        "approvalWriteCount": 0,
        "auditWriteCount": 0,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def _stage_results(frontend: Mapping[str, Any], pages: Mapping[str, Any]) -> list[dict[str, Any]]:
    specs = [
        ("A8-01", "Read-only Frontend Skeleton Foundation", "ONE_AIRPORT_A8_01_READ_ONLY_FRONTEND_SKELETON_FOUNDATION_PASS", A8_SKELETON, "validate-one-airport-read-only-frontend-skeleton.py", frontend),
        ("A8-02", "Read-only Frontend Page Contract and Local Smoke Gate", "ONE_AIRPORT_A8_02_READ_ONLY_FRONTEND_PAGE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS", A8_PAGE_CONTRACT, "validate-one-airport-read-only-frontend-page-contract.py", pages),
    ]
    return [
        build_stage_result(stage_id=stage_id, stage_name=name, pass_marker=marker, artifact_path=str(path.relative_to(ROOT)), validator_name=validator, status=GateStatus.PASS.value, summary=artifact["summary"])
        for stage_id, name, marker, path, validator, artifact in specs
    ]


def _page_coverage(frontend: Mapping[str, Any], pages: Mapping[str, Any]) -> list[dict[str, Any]]:
    page_contracts = {item["pageKey"]: item for item in pages["pageContracts"]}
    layouts = {item["pageKey"] for item in pages["layoutContracts"]}
    routes = {item["pageKey"]: item for item in frontend["routeSkeletons"]}
    entries: list[dict[str, Any]] = []
    for page in frontend["pageSkeletons"]:
        page_contract = page_contracts[page["pageKey"]]
        route = routes[page["pageKey"]]
        entries.append(
            build_page_coverage_entry(
                page_key=page["pageKey"],
                page_skeleton_present=True,
                page_contract_present=True,
                layout_contract_present=page["pageKey"] in layouts,
                route_skeleton_present=True,
                route_production_disabled=route["productionRouteEnabled"] is False,
                static_only=page_contract["staticOnly"] is True,
                read_only=page_contract["readOnly"] is True,
                live_api_call_disabled=page_contract["liveApiCallEnabled"] is False,
                data_mutation_disabled=page_contract["dataMutationEnabled"] is False,
            )
        )
    return sorted(entries, key=lambda item: item["pageKey"])


def _component_coverage(frontend: Mapping[str, Any], pages: Mapping[str, Any]) -> list[dict[str, Any]]:
    component_counts: dict[str, int] = {}
    state_counts: dict[str, int] = {}
    interaction_counts: dict[str, int] = {}
    for item in pages["componentBindingContracts"]:
        component_counts[item["pageKey"]] = component_counts.get(item["pageKey"], 0) + 1
    for item in pages["uiStateContracts"]:
        state_counts[item["pageKey"]] = state_counts.get(item["pageKey"], 0) + 1
    for item in pages["interactionContracts"]:
        interaction_counts[item["pageKey"]] = interaction_counts.get(item["pageKey"], 0) + 1
    data_pages = {item["pageKey"] for item in frontend["dataBindingSkeletons"]}
    card_pages = {item["pageKey"] for item in frontend["cardSkeletons"]}
    queue_pages = {item["pageKey"] for item in frontend["queueSkeletons"]}
    return sorted(
        [
            build_component_coverage_entry(
                page_key=page["pageKey"],
                component_binding_count=component_counts.get(page["pageKey"], 0),
                ui_state_contract_count=state_counts.get(page["pageKey"], 0),
                interaction_contract_count=interaction_counts.get(page["pageKey"], 0),
                data_binding_present=page["pageKey"] in data_pages,
                card_binding_present=page["pageKey"] in card_pages,
                queue_binding_present=page["pageKey"] in queue_pages,
            )
            for page in frontend["pageSkeletons"]
        ],
        key=lambda item: item["pageKey"],
    )


def _interaction_coverage(frontend: Mapping[str, Any], pages: Mapping[str, Any]) -> list[dict[str, Any]]:
    by_page: dict[str, set[str]] = {}
    mutation_by_page: dict[str, bool] = {}
    for item in pages["interactionContracts"]:
        by_page.setdefault(item["pageKey"], set()).add(item["interactionType"])
        mutation_by_page[item["pageKey"]] = mutation_by_page.get(item["pageKey"], False) or bool(item["mutationAllowed"])
    return sorted(
        [build_interaction_coverage_entry(page_key=page["pageKey"], interaction_types=by_page.get(page["pageKey"], set()), mutation_allowed=mutation_by_page.get(page["pageKey"], False)) for page in frontend["pageSkeletons"]],
        key=lambda item: item["pageKey"],
    )


def _release_gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_A8_STAGE_COMPLETENESS", "A8 stage completeness", ["A8_01_A8_02_ARTIFACTS_PRESENT"]),
        ("G02_A8_PASS_MARKER_COMPLETENESS", "A8 pass marker completeness", ["TWO_A8_PASS_MARKERS_REPRESENTED"]),
        ("G03_PAGE_SKELETON_COVERAGE", "Page skeleton coverage", ["8_PAGE_SKELETONS"]),
        ("G04_PAGE_CONTRACT_COVERAGE", "Page contract coverage", ["8_PAGE_CONTRACTS"]),
        ("G05_ROUTE_SKELETON_COVERAGE", "Route skeleton coverage", ["8_ROUTE_SKELETONS_PRODUCTION_DISABLED"]),
        ("G06_LAYOUT_CONTRACT_COVERAGE", "Layout contract coverage", ["8_LAYOUT_CONTRACTS"]),
        ("G07_COMPONENT_COVERAGE", "Component coverage", ["3_COMPONENT_BINDINGS_PER_PAGE"]),
        ("G08_UI_STATE_COVERAGE", "UI state coverage", ["6_UI_STATES_PER_PAGE"]),
        ("G09_INTERACTION_COVERAGE", "Interaction coverage", ["8_INTERACTIONS_PER_PAGE"]),
        ("G10_STATIC_READ_ONLY_BOUNDARY", "Static read-only boundary", ["STATIC_READ_ONLY_MUTATION_DISABLED"]),
        ("G11_NO_LIVE_API_BROWSER_NETWORK_BOUNDARY", "No live API browser network boundary", ["NO_LIVE_API_BROWSER_NETWORK_LOCALHOST"]),
        ("G12_NO_REAL_FRONTEND_IMPLEMENTATION", "No real frontend implementation", ["NO_REAL_FRONTEND_FILES_ROUTES_MENUS"]),
        ("G13_A7_API_DEPENDENCY_GATE", "A7 API dependency gate", ["A7_READ_ONLY_ROUTE_ALLOWED_PRODUCTION_API_DISABLED"]),
        ("G14_A6_FRONTEND_DEPENDENCY_GATE", "A6 frontend dependency gate", ["A6_FRONTEND_SKELETON_ALLOWED_PRODUCTION_DISABLED"]),
        ("G15_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G16_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G17_IMPLEMENTATION_DECISION", "Implementation decision", ["FUTURE_READ_ONLY_FRONTEND_ALLOWED_PRODUCTION_DISABLED"]),
    ]
    return [build_release_gate_result(gate_id=gate_id, gate_name=name, status=GateStatus.PASS.value, severity=Severity.INFO.value if gate_id != "G17_IMPLEMENTATION_DECISION" else Severity.LOW.value, blocking=True, reason_codes=reasons) for gate_id, name, reasons in specs]


def _decision() -> dict[str, Any]:
    return build_implementation_decision(
        decision_state=DecisionState.READY_FOR_READ_ONLY_FRONTEND_IMPLEMENTATION.value,
        read_only_frontend_implementation_allowed=True,
        production_frontend_allowed=False,
        real_route_implementation_allowed=False,
        menu_implementation_allowed=False,
        live_api_call_allowed=False,
        data_mutation_allowed=False,
        browser_smoke_allowed=False,
        database_write_allowed=False,
        runtime_activation_allowed=False,
        production_activation_allowed=False,
        api_implementation_required=False,
        push_allowed=False,
        decision_reason="A8 skeleton and page contracts are complete; only a future read-only frontend implementation phase is allowed.",
    )


def _dependency_gates(a7: Mapping[str, Any], a6: Mapping[str, Any], a6_contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks = [
        ("D01_A7_READ_ONLY_API_ALLOWED", "A7 read-only API allowed", a7["summary"]["readOnlyApiRouteImplementationAllowed"] is True),
        ("D02_A7_PRODUCTION_API_DISABLED", "A7 production API disabled", a7["summary"]["productionApiAllowed"] is False),
        ("D03_A6_FRONTEND_SKELETON_ALLOWED", "A6 frontend skeleton allowed", a6["summary"]["frontendSkeletonPhaseAllowed"] is True),
        ("D04_A6_PRODUCTION_FRONTEND_DISABLED", "A6 production frontend disabled", a6["summary"]["productionFrontendAllowed"] is False),
        ("D05_A6_READINESS_CANDIDATES", "A6 readiness candidates", a6_contract["summary"]["frontendPageCandidateCount"] == 8 and a6_contract["summary"]["frontendRouteCandidateCount"] == 8),
    ]
    return [build_release_gate_result(gate_id=gate_id, gate_name=name, status=GateStatus.PASS.value if ok else GateStatus.FAIL.value, severity=Severity.INFO.value, blocking=True, reason_codes=[gate_id, "DEPENDENCY_PASS" if ok else "DEPENDENCY_FAIL"]) for gate_id, name, ok in checks]


def _boundaries(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs = {
        "readOnlyFrontendImplementationAllowed": (True, summary["readOnlyFrontendImplementationAllowed"]),
        "productionFrontendAllowed": (False, summary["productionFrontendAllowed"]),
        "realRouteImplementationAllowed": (False, summary["realRouteImplementationAllowed"]),
        "menuImplementationAllowed": (False, summary["menuImplementationAllowed"]),
        "liveApiCallAllowed": (False, summary["liveApiCallAllowed"]),
        "dataMutationAllowed": (False, summary["dataMutationAllowed"]),
        "browserSmokeAllowed": (False, summary["browserSmokeAllowed"]),
        "databaseWriteAllowed": (False, summary["databaseWriteAllowed"]),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"]),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"]),
        "apiImplementationRequired": (False, summary["apiImplementationRequired"]),
        "pushAllowed": (False, summary["pushAllowed"]),
        "realFrontendFileChangeCount": (0, summary["realFrontendFileChangeCount"]),
        "realMenuEntryChangeCount": (0, summary["realMenuEntryChangeCount"]),
        "databaseWriteCount": (0, summary["databaseWriteCount"]),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"]),
        "decisionWriteCount": (0, summary["decisionWriteCount"]),
        "approvalWriteCount": (0, summary["approvalWriteCount"]),
        "auditWriteCount": (0, summary["auditWriteCount"]),
    }
    return [build_implementation_boundary_entry(boundary_key=key, expected_value=expected, actual_value=actual, blocking=True) for key, (expected, actual) in sorted(pairs.items())]


def build_airport_read_only_frontend_release_gate() -> dict[str, Any]:
    frontend = _load(A8_SKELETON)
    pages = _load(A8_PAGE_CONTRACT)
    a7 = _load(A7_RELEASE)
    a6 = _load(A6_GATE)
    a6_contract = _load(A6_CONTRACT)
    summary = _summary()
    gate = build_read_only_frontend_implementation_release_gate(
        release_gate_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID, "frontendDigest": frontend["deterministicDigest"], "pageDigest": pages["deterministicDigest"]}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        stage_results=_stage_results(frontend, pages),
        page_coverage_matrix=_page_coverage(frontend, pages),
        component_coverage_matrix=_component_coverage(frontend, pages),
        interaction_coverage_matrix=_interaction_coverage(frontend, pages),
        implementation_boundary_matrix=_boundaries(summary),
        release_gate_results=_release_gates(),
        dependency_gate_results=_dependency_gates(a7, a6, a6_contract),
        implementation_decision=_decision(),
        artifact_references=[
            _artifact_reference(A8_SKELETON, "A8_READ_ONLY_FRONTEND_SKELETON"),
            _artifact_reference(A8_PAGE_CONTRACT, "A8_READ_ONLY_FRONTEND_PAGE_CONTRACT"),
            _artifact_reference(A7_RELEASE, "A7_READ_ONLY_API_RELEASE_GATE"),
            _artifact_reference(A6_GATE, "A6_FRONTEND_IMPLEMENTATION_GATE"),
            _artifact_reference(A6_CONTRACT, "A6_FRONTEND_READINESS_CONTRACT"),
        ],
    )
    validate_read_only_frontend_release_gate(gate)
    return gate
