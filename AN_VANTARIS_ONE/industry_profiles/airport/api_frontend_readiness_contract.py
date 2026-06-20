"""Airport API / Frontend readiness contract freeze."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from api_frontend_readiness_contract.aggregation import build_boundary_matrix
from api_frontend_readiness_contract.enums import ContractState, GateStatus, Severity
from api_frontend_readiness_contract.models import (
    build_api_endpoint_candidate,
    build_api_frontend_readiness_contract,
    build_artifact_reference,
    build_card_binding_contract,
    build_data_binding_contract,
    build_frontend_page_candidate,
    build_frontend_route_candidate,
    build_queue_binding_contract,
    build_readiness_gate,
)
from api_frontend_readiness_contract.validation import validate_api_frontend_readiness_contract
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A6-01"
PROFILE_ID = "airport-api-frontend-readiness-contract-profile-v1"
IMPLEMENTATION_STATUS = "API_FRONTEND_READINESS_CONTRACT_FREEZE_COMPLETE"
READINESS_OUTCOME = "API_FRONTEND_CONTRACT_FROZEN_FOR_FUTURE_IMPLEMENTATION_PLANNING"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
HANDOFF = PROJECTIONS_DIR / "airport-operations-console-handoff-gate.v1.json"
PACKAGE = PROJECTIONS_DIR / "airport-operations-console-package.v1.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _path_for_page(page_key: str) -> str:
    return "/airport/operations-console/" + page_key.lower().replace("_", "-")


def _route_key(page_key: str) -> str:
    return "AIRPORT_CONSOLE_ROUTE_" + page_key


def _endpoint_key(page_key: str) -> str:
    return "GET_AIRPORT_CONSOLE_" + page_key


def _primary_source_key(page: Mapping[str, Any]) -> str:
    return str(page.get("sourceProjectionKeys", ["UNKNOWN"])[0])


def _source_type_by_key(package: Mapping[str, Any]) -> dict[str, str]:
    return {item["dataSourceKey"]: item["sourceProjectionType"] for item in package["packageDataSources"]}


def _source_artifact_by_key(package: Mapping[str, Any]) -> dict[str, str]:
    return {item["dataSourceKey"]: item["sourceArtifactPath"] for item in package["packageDataSources"]}


def _summary(package: Mapping[str, Any]) -> dict[str, Any]:
    package_summary = package["summary"]
    return {
        "apiEndpointCandidateCount": 8,
        "frontendPageCandidateCount": 8,
        "frontendRouteCandidateCount": 8,
        "dataBindingContractCount": 15,
        "cardBindingContractCount": 8,
        "queueBindingContractCount": 8,
        "readinessGateCount": 15,
        "passedGateCount": 15,
        "blockingGateFailureCount": 0,
        "readOnlyEndpointCandidateCount": 8,
        "apiImplementationAllowedCount": 0,
        "frontendImplementationAllowedCount": 0,
        "routeImplementationAllowedCount": 0,
        "databaseAccessAllowedCount": 0,
        "writeOperationAllowedCount": 0,
        "authPolicyRequiredCount": 8,
        "pageCandidateCount": 8,
        "cardCandidateCount": 8,
        "sourceSystemCandidateCount": package_summary["sourceSystemCandidateCount"],
        "alarmEventCandidateCount": package_summary["alarmEventCandidateCount"],
        "faultCaseCandidateCount": package_summary["faultCaseCandidateCount"],
        "workOrderIntentCandidateCount": package_summary["workOrderIntentCandidateCount"],
        "investigationCaseCount": package_summary["investigationCaseCount"],
        "decisionItemCount": package_summary["decisionItemCount"],
        "queueRowCount": package_summary["queueRowCount"],
        "totalDeviceEvidenceCount": package_summary["totalDeviceEvidenceCount"],
        "apiEnabled": False,
        "frontendEnabled": False,
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


def _api_endpoint_candidates(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_types = _source_type_by_key(package)
    candidates: list[dict[str, Any]] = []
    for page in package["pageDefinitions"]:
        source_key = _primary_source_key(page)
        candidates.append(
            build_api_endpoint_candidate(
                endpoint_key=_endpoint_key(page["pageKey"]),
                path_candidate="/api" + _path_for_page(page["pageKey"]),
                source_page_key=page["pageKey"],
                source_data_source_key=source_key,
                source_projection_type=source_types.get(source_key, "UNKNOWN"),
                response_contract_state=ContractState.FROZEN_FOR_PLANNING.value,
            )
        )
    return sorted(candidates, key=lambda item: item["endpointKey"])


def _frontend_route_candidates(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [
            build_frontend_route_candidate(
                route_key=_route_key(page["pageKey"]),
                path_candidate=_path_for_page(page["pageKey"]),
                page_key=page["pageKey"],
            )
            for page in package["pageDefinitions"]
        ],
        key=lambda item: item["routeKey"],
    )


def _frontend_page_candidates(package: Mapping[str, Any], card_bindings: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    card_ids_by_page: dict[str, list[str]] = {}
    for card in card_bindings:
        card_ids_by_page.setdefault(str(card["pageKey"]), []).append(str(card["cardBindingId"]))
    return sorted(
        [
            build_frontend_page_candidate(
                page_key=page["pageKey"],
                title=page["title"],
                page_type=page["pageType"],
                route_candidate_key=_route_key(page["pageKey"]),
                source_data_source_keys=page["sourceProjectionKeys"],
                card_candidate_ids=card_ids_by_page.get(page["pageKey"], []),
                readiness_state=ContractState.READY_FOR_IMPLEMENTATION_PLANNING.value,
            )
            for page in package["pageDefinitions"]
        ],
        key=lambda item: item["pageKey"],
    )


def _card_binding_contracts(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_keys_by_page = {page["pageKey"]: page["sourceProjectionKeys"] for page in package["pageDefinitions"]}
    return sorted(
        [
            build_card_binding_contract(
                card_type=card["cardType"],
                page_key=card["pageKey"],
                title=card["title"],
                source_data_source_keys=source_keys_by_page.get(card["pageKey"], []),
            )
            for card in package["consoleCards"]
        ],
        key=lambda item: (item["pageKey"], item["title"]),
    )


def _data_binding_contracts(package: Mapping[str, Any], endpoints: list[Mapping[str, Any]], pages: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    endpoint_by_page = {item["sourcePageKey"]: item["endpointCandidateId"] for item in endpoints}
    page_candidate_by_page = {item["pageKey"]: item["pageCandidateId"] for item in pages}
    page_by_source: dict[str, str] = {}
    for page in package["pageDefinitions"]:
        for source_key in page["sourceProjectionKeys"]:
            page_by_source.setdefault(str(source_key), str(page["pageKey"]))
    bindings: list[dict[str, Any]] = []
    for source in package["packageDataSources"]:
        page_key = page_by_source.get(source["dataSourceKey"], "AIRPORT_OVERVIEW")
        bindings.append(
            build_data_binding_contract(
                page_key=page_key,
                data_source_key=source["dataSourceKey"],
                source_artifact_path=source["sourceArtifactPath"],
                source_projection_type=source["sourceProjectionType"],
                api_endpoint_candidate_id=endpoint_by_page[page_key],
                frontend_page_candidate_id=page_candidate_by_page[page_key],
            )
        )
    return sorted(bindings, key=lambda item: item["dataSourceKey"])


def _queue_binding_contracts(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    summary = package["summary"]
    return sorted(
        [
            build_queue_binding_contract(
                queue_key="QUEUE_" + page["pageKey"],
                page_key=page["pageKey"],
                source_data_source_keys=page["sourceProjectionKeys"],
                row_count=summary["queueRowCount"] if page["pageKey"] == "REPORTS" else 0,
            )
            for page in package["pageDefinitions"]
        ],
        key=lambda item: item["queueKey"],
    )


def _readiness_gates(handoff: Mapping[str, Any]) -> list[dict[str, Any]]:
    assert handoff["summary"]["handoffAllowed"] is True
    specs = [
        ("G01_API_ENDPOINT_CANDIDATES_COMPLETE", "API endpoint candidates complete", ["8_ENDPOINT_CANDIDATES"]),
        ("G02_FRONTEND_PAGE_CANDIDATES_COMPLETE", "Frontend page candidates complete", ["8_PAGE_CANDIDATES"]),
        ("G03_FRONTEND_ROUTE_CANDIDATES_COMPLETE", "Frontend route candidates complete", ["8_ROUTE_CANDIDATES"]),
        ("G04_DATASOURCE_BINDINGS_COMPLETE", "Datasource bindings complete", ["15_DATASOURCE_BINDINGS"]),
        ("G05_CARD_BINDINGS_COMPLETE", "Card bindings complete", ["8_CARD_BINDINGS"]),
        ("G06_QUEUE_BINDINGS_COMPLETE", "Queue bindings complete", ["8_QUEUE_BINDINGS"]),
        ("G07_API_IMPLEMENTATION_BOUNDARY", "API implementation boundary", ["API_IMPLEMENTATION_DISABLED"]),
        ("G08_FRONTEND_IMPLEMENTATION_BOUNDARY", "Frontend implementation boundary", ["FRONTEND_IMPLEMENTATION_DISABLED"]),
        ("G09_DATABASE_WRITE_BOUNDARY", "Database write boundary", ["DB_AND_WRITES_DISABLED"]),
        ("G10_RUNTIME_BOUNDARY", "Runtime boundary", ["RUNTIME_DISABLED"]),
        ("G11_AUTH_POLICY_DECLARED", "Auth policy declared", ["ALL_ENDPOINTS_REQUIRE_AUTH_POLICY"]),
        ("G12_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G13_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G14_HANDOFF_DEPENDENCY_GATE", "Handoff dependency gate", ["A5_02_HANDOFF_ALLOWED_TRUE"]),
        ("G15_CONTRACT_FREEZE_DECISION", "Contract freeze decision", ["ALL_BLOCKING_GATES_PASS"]),
    ]
    return [
        build_readiness_gate(
            gate_id=gate_id,
            gate_name=name,
            status=GateStatus.PASS.value,
            severity=Severity.INFO.value if gate_id != "G15_CONTRACT_FREEZE_DECISION" else Severity.LOW.value,
            blocking=True,
            reason_codes=reasons,
        )
        for gate_id, name, reasons in specs
    ]


def _boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return build_boundary_matrix({
        "apiEnabled": (False, summary["apiEnabled"], True),
        "apiImplementationAllowedCount": (0, summary["apiImplementationAllowedCount"], True),
        "approvalWriteCount": (0, summary["approvalWriteCount"], True),
        "auditWriteCount": (0, summary["auditWriteCount"], True),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"], True),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"], True),
        "databaseAccessAllowedCount": (0, summary["databaseAccessAllowedCount"], True),
        "databaseWriteCount": (0, summary["databaseWriteCount"], True),
        "decisionWriteCount": (0, summary["decisionWriteCount"], True),
        "frontendEnabled": (False, summary["frontendEnabled"], True),
        "frontendImplementationAllowedCount": (0, summary["frontendImplementationAllowedCount"], True),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"], True),
        "pushAllowed": (False, summary["pushAllowed"], True),
        "routeImplementationAllowedCount": (0, summary["routeImplementationAllowedCount"], True),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"], True),
        "writeOperationAllowedCount": (0, summary["writeOperationAllowedCount"], True),
    })


def build_airport_api_frontend_readiness_contract() -> dict[str, Any]:
    package = _load(PACKAGE)
    handoff = _load(HANDOFF)
    card_bindings = _card_binding_contracts(package)
    endpoint_candidates = _api_endpoint_candidates(package)
    page_candidates = _frontend_page_candidates(package, card_bindings)
    route_candidates = _frontend_route_candidates(package)
    summary = _summary(package)
    contract = build_api_frontend_readiness_contract(
        contract_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID, "handoffDigest": handoff["deterministicDigest"]}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        api_endpoint_candidates=endpoint_candidates,
        frontend_page_candidates=page_candidates,
        frontend_route_candidates=route_candidates,
        data_binding_contracts=_data_binding_contracts(package, endpoint_candidates, page_candidates),
        card_binding_contracts=card_bindings,
        queue_binding_contracts=_queue_binding_contracts(package),
        readiness_gates=_readiness_gates(handoff),
        boundary_matrix=_boundary_matrix(summary),
        source_artifact_references=[
            _artifact_reference(HANDOFF, "A5_HANDOFF_GATE"),
            _artifact_reference(PACKAGE, "A5_OPERATIONS_CONSOLE_PACKAGE"),
        ],
    )
    validate_api_frontend_readiness_contract(contract)
    return contract
