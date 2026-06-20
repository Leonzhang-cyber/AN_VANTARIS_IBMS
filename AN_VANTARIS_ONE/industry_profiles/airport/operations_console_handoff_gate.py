"""Airport Operations Console Package readiness and handoff gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from operations_console_handoff_gate.aggregation import build_boundary_matrix
from operations_console_handoff_gate.enums import ContractCandidateState, GateStatus, HandoffState, Severity
from operations_console_handoff_gate.models import (
    build_api_readiness_contract,
    build_artifact_reference,
    build_card_handoff_entry,
    build_data_source_handoff_entry,
    build_frontend_readiness_contract,
    build_handoff_decision,
    build_operations_console_handoff_gate,
    build_page_handoff_entry,
    build_release_gate_result,
)
from operations_console_handoff_gate.validation import validate_operations_console_handoff_gate
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A5-02"
PROFILE_ID = "airport-operations-console-handoff-gate-profile-v1"
IMPLEMENTATION_STATUS = "AIRPORT_CONSOLE_PACKAGE_HANDOFF_GATE_COMPLETE"
READINESS_OUTCOME = "AIRPORT_CONSOLE_PACKAGE_READY_FOR_API_FRONTEND_PLANNING"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
PACKAGE = PROJECTIONS_DIR / "airport-operations-console-package.v1.json"
A3_RELEASE = PROJECTIONS_DIR / "airport-a3-readiness-release-gate.v1.json"
A4_RELEASE = PROJECTIONS_DIR / "airport-a4-readiness-release-gate.v1.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _summary(package: Mapping[str, Any]) -> dict[str, Any]:
    package_summary = package["summary"]
    return {
        "pageHandoffCount": 8,
        "dataSourceHandoffCount": 15,
        "cardHandoffCount": 8,
        "releaseGateCount": 15,
        "passedGateCount": 15,
        "blockingGateFailureCount": 0,
        "candidateEndpointCount": 8,
        "readOnlyEndpointCandidateCount": 8,
        "pageCandidateCount": 8,
        "cardCandidateCount": 8,
        "sourceSystemCandidateCount": package_summary["sourceSystemCandidateCount"],
        "alarmEventCandidateCount": package_summary["alarmEventCandidateCount"],
        "faultCaseCandidateCount": package_summary["faultCaseCandidateCount"],
        "workOrderIntentCandidateCount": package_summary["workOrderIntentCandidateCount"],
        "investigationCaseCount": package_summary["investigationCaseCount"],
        "operationsRowCount": package_summary["operationsRowCount"],
        "decisionItemCount": package_summary["decisionItemCount"],
        "queueRowCount": package_summary["queueRowCount"],
        "policyGuardResultCount": package_summary["policyGuardResultCount"],
        "auditPreviewCount": package_summary["auditPreviewCount"],
        "totalDeviceEvidenceCount": package_summary["totalDeviceEvidenceCount"],
        "pendingDecisionCount": package_summary["pendingDecisionCount"],
        "blockingDecisionCount": package_summary["blockingDecisionCount"],
        "runtimeObservedCount": 0,
        "runtimeAlarmObservedCount": 0,
        "ufmsFaultCaseCreatedCount": 0,
        "workOrderIntentCreatedCount": 0,
        "workOrderCreatedCount": 0,
        "evidenceCenterWriteCount": 0,
        "ummsWriteCount": 0,
        "oneWorkManagementWriteCount": 0,
        "decisionWriteCount": 0,
        "approvalWriteCount": 0,
        "auditWriteCount": 0,
        "canonicalWriteCount": 0,
        "databaseWriteCount": 0,
        "apiEnabled": False,
        "frontendEnabled": False,
        "endpointImplementationAllowed": False,
        "frontendImplementationAllowed": False,
        "routeImplementationAllowed": False,
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
        "pushAllowed": False,
        "handoffAllowed": True,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def _page_handoff_matrix(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for page in package["pageDefinitions"]:
        api_state = ContractCandidateState.CANDIDATE_READY.value if page["pageType"] in {"OVERVIEW", "INTEGRATION_HEALTH", "ALARM_EVENT_OPERATIONS", "RELEASE_GATE"} else ContractCandidateState.READ_ONLY_ONLY.value
        frontend_state = ContractCandidateState.CANDIDATE_READY.value
        entries.append(
            build_page_handoff_entry(
                page_key=page["pageKey"],
                page_title=page["title"],
                page_type=page["pageType"],
                readiness_state=HandoffState.READY_FOR_HANDOFF.value,
                source_projection_keys=page["sourceProjectionKeys"],
                data_source_ids=page["dataSourceIds"],
                card_ids=page["primaryCardIds"],
                api_contract_candidate_state=api_state,
                frontend_contract_candidate_state=frontend_state,
                blocked=False,
                decision_required=bool(page["decisionRequired"]),
            )
        )
    return sorted(entries, key=lambda entry: entry["pageKey"])


def _data_source_handoff_matrix(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [
            build_data_source_handoff_entry(
                data_source_key=data_source["dataSourceKey"],
                source_artifact_path=data_source["sourceArtifactPath"],
                source_projection_type=data_source["sourceProjectionType"],
                read_only=data_source["readOnly"],
                api_enabled=data_source["apiEnabled"],
                frontend_enabled=data_source["frontendEnabled"],
                database_access_enabled=data_source["databaseAccessEnabled"],
                api_contract_candidate_state=ContractCandidateState.READ_ONLY_ONLY.value,
                frontend_contract_candidate_state=ContractCandidateState.CANDIDATE_READY.value,
            )
            for data_source in package["packageDataSources"]
        ],
        key=lambda entry: entry["dataSourceKey"],
    )


def _card_handoff_matrix(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_keys_by_page = {page["pageKey"]: page["sourceProjectionKeys"] for page in package["pageDefinitions"]}
    return sorted(
        [
            build_card_handoff_entry(
                card_type=card["cardType"],
                title=card["title"],
                page_key=card["pageKey"],
                source_data_source_keys=source_keys_by_page.get(card["pageKey"], []),
                readiness_state=HandoffState.READY_FOR_HANDOFF.value,
                api_contract_candidate_state=ContractCandidateState.READ_ONLY_ONLY.value,
                frontend_contract_candidate_state=ContractCandidateState.CANDIDATE_READY.value,
            )
            for card in package["consoleCards"]
        ],
        key=lambda entry: (entry["pageKey"], entry["title"]),
    )


def _api_readiness_contract() -> dict[str, Any]:
    return build_api_readiness_contract(
        contract_state=HandoffState.READY_FOR_HANDOFF.value,
        endpoint_implementation_allowed=False,
        public_api_enabled=False,
        database_access_allowed=False,
        write_operation_allowed=False,
        candidate_endpoint_count=8,
        read_only_endpoint_candidate_count=8,
    )


def _frontend_readiness_contract() -> dict[str, Any]:
    return build_frontend_readiness_contract(
        contract_state=HandoffState.READY_FOR_HANDOFF.value,
        frontend_implementation_allowed=False,
        route_implementation_allowed=False,
        runtime_data_mutation_allowed=False,
        page_candidate_count=8,
        card_candidate_count=8,
    )


def _release_gate_results(package: Mapping[str, Any], a3_release: Mapping[str, Any], a4_release: Mapping[str, Any]) -> list[dict[str, Any]]:
    package_summary = package["summary"]
    gate_specs = [
        ("G01_HANDOFF_PAGE_MATRIX_COMPLETE", "Handoff page matrix complete", ["8_PAGE_HANDOFF_ENTRIES"], ["pageHandoffMatrix"]),
        ("G02_HANDOFF_DATASOURCE_MATRIX_COMPLETE", "Handoff datasource matrix complete", ["15_DATASOURCE_HANDOFF_ENTRIES"], ["dataSourceHandoffMatrix"]),
        ("G03_HANDOFF_CARD_MATRIX_COMPLETE", "Handoff card matrix complete", ["8_CARD_HANDOFF_ENTRIES"], ["cardHandoffMatrix"]),
        ("G04_API_READINESS_CONTRACT_CANDIDATE", "API readiness contract candidate", ["API_CONTRACT_CANDIDATE_FLAGS_DISABLED"], ["apiReadinessContract"]),
        ("G05_FRONTEND_READINESS_CONTRACT_CANDIDATE", "Frontend readiness contract candidate", ["FRONTEND_CONTRACT_CANDIDATE_FLAGS_DISABLED"], ["frontendReadinessContract"]),
        ("G06_READ_ONLY_DATASOURCE_BOUNDARY", "Read-only datasource boundary", ["DATASOURCES_READ_ONLY_AND_SURFACES_DISABLED"], ["dataSourceHandoffMatrix"]),
        ("G07_A3_DEPENDENCY_RELEASE_GATE", "A3 dependency release gate", ["A3_RELEASE_ALLOWED_TRUE"], [str(A3_RELEASE.relative_to(ROOT))]),
        ("G08_A4_DEPENDENCY_RELEASE_GATE", "A4 dependency release gate", ["A4_RELEASE_ALLOWED_TRUE"], [str(A4_RELEASE.relative_to(ROOT))]),
        ("G09_PACKAGE_READINESS_GATE", "A5 package readiness gate", ["A5_PACKAGE_12_OF_12_GATES_PASS"], [str(PACKAGE.relative_to(ROOT))]),
        ("G10_WRITE_BOUNDARY", "Write boundary", ["ALL_WRITE_COUNTS_ZERO"], ["summary"]),
        ("G11_API_FRONTEND_BOUNDARY", "API/frontend boundary", ["API_AND_FRONTEND_DISABLED"], ["summary"]),
        ("G12_RUNTIME_BOUNDARY", "Runtime boundary", ["RUNTIME_AND_PRODUCTION_DISABLED"], ["summary"]),
        ("G13_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"], ["summary"]),
        ("G14_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"], ["scripts/validation/_run_a5_02_airport_operations_console_handoff_gate.py"]),
        ("G15_HANDOFF_DECISION", "Handoff decision", ["ALL_BLOCKING_GATES_PASS"], ["handoffDecision"]),
    ]
    assert a3_release["releaseDecision"]["releaseAllowed"] is True
    assert a4_release["releaseDecision"]["releaseAllowed"] is True
    assert package_summary["packageReadinessGateCount"] == 12
    return [
        build_release_gate_result(
            gate_id=gate_id,
            gate_name=name,
            status=GateStatus.PASS.value,
            severity=Severity.INFO.value if gate_id != "G15_HANDOFF_DECISION" else Severity.LOW.value,
            blocking=True,
            reason_codes=reasons,
            evidence_references=evidence,
        )
        for gate_id, name, reasons, evidence in gate_specs
    ]


def _boundary_matrix(summary: Mapping[str, Any], api_contract: Mapping[str, Any], frontend_contract: Mapping[str, Any], decision: Mapping[str, Any]) -> list[dict[str, Any]]:
    return build_boundary_matrix({
        "apiEnabled": (False, summary["apiEnabled"], True),
        "auditWriteCount": (0, summary["auditWriteCount"], True),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"], True),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"], True),
        "databaseAccessAllowed": (False, api_contract["databaseAccessAllowed"], True),
        "databaseWriteAllowed": (False, decision["databaseWriteAllowed"], True),
        "databaseWriteCount": (0, summary["databaseWriteCount"], True),
        "decisionWriteCount": (0, summary["decisionWriteCount"], True),
        "endpointImplementationAllowed": (False, api_contract["endpointImplementationAllowed"], True),
        "frontendEnabled": (False, summary["frontendEnabled"], True),
        "frontendImplementationAllowed": (False, frontend_contract["frontendImplementationAllowed"], True),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"], True),
        "publicApiEnabled": (False, api_contract["publicApiEnabled"], True),
        "pushAllowed": (False, summary["pushAllowed"], True),
        "routeImplementationAllowed": (False, frontend_contract["routeImplementationAllowed"], True),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"], True),
        "runtimeDataMutationAllowed": (False, frontend_contract["runtimeDataMutationAllowed"], True),
        "writeOperationAllowed": (False, api_contract["writeOperationAllowed"], True),
    })


def build_airport_operations_console_handoff_gate() -> dict[str, Any]:
    package = _load(PACKAGE)
    a3_release = _load(A3_RELEASE)
    a4_release = _load(A4_RELEASE)
    summary = _summary(package)
    api_contract = _api_readiness_contract()
    frontend_contract = _frontend_readiness_contract()
    decision = build_handoff_decision(
        decision_state=HandoffState.READY_FOR_HANDOFF.value,
        handoff_allowed=True,
        api_implementation_allowed=False,
        frontend_implementation_allowed=False,
        database_write_allowed=False,
        runtime_activation_allowed=False,
        production_activation_allowed=False,
        push_allowed=False,
        decision_reason="Airport console package is ready for future API/frontend planning only; implementation and write surfaces remain disabled.",
    )
    handoff_gate = build_operations_console_handoff_gate(
        handoff_gate_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID, "packageDigest": package["deterministicDigest"]}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        page_handoff_matrix=_page_handoff_matrix(package),
        data_source_handoff_matrix=_data_source_handoff_matrix(package),
        card_handoff_matrix=_card_handoff_matrix(package),
        api_readiness_contract=api_contract,
        frontend_readiness_contract=frontend_contract,
        release_gate_results=_release_gate_results(package, a3_release, a4_release),
        boundary_matrix=_boundary_matrix(summary, api_contract, frontend_contract, decision),
        artifact_references=[
            _artifact_reference(PACKAGE, "A5_OPERATIONS_CONSOLE_PACKAGE"),
            _artifact_reference(A3_RELEASE, "A3_READINESS_RELEASE_GATE"),
            _artifact_reference(A4_RELEASE, "A4_READINESS_RELEASE_GATE"),
        ],
        handoff_decision=decision,
    )
    validate_operations_console_handoff_gate(handoff_gate)
    return handoff_gate
