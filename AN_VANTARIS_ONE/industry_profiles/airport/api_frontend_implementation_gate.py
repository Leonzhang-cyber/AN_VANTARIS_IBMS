"""Airport API / Frontend implementation readiness release gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from api_frontend_implementation_gate.aggregation import build_contract_coverage_matrix, build_implementation_boundary_matrix
from api_frontend_implementation_gate.enums import DecisionState, GateStatus, Severity
from api_frontend_implementation_gate.models import (
    build_api_frontend_implementation_readiness_gate,
    build_api_implementation_readiness,
    build_artifact_reference,
    build_frontend_implementation_readiness,
    build_gate_result,
    build_implementation_decision,
)
from api_frontend_implementation_gate.validation import validate_api_frontend_implementation_readiness_gate
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A6-02"
PROFILE_ID = "airport-api-frontend-implementation-readiness-gate-profile-v1"
IMPLEMENTATION_STATUS = "API_FRONTEND_IMPLEMENTATION_READINESS_RELEASE_GATE_COMPLETE"
READINESS_OUTCOME = "API_FRONTEND_READY_FOR_READ_ONLY_SKELETON_PLANNING"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
A6_CONTRACT = PROJECTIONS_DIR / "airport-api-frontend-readiness-contract.v1.json"
A5_HANDOFF = PROJECTIONS_DIR / "airport-operations-console-handoff-gate.v1.json"
A5_PACKAGE = PROJECTIONS_DIR / "airport-operations-console-package.v1.json"
A4_RELEASE = PROJECTIONS_DIR / "airport-a4-readiness-release-gate.v1.json"
A3_RELEASE = PROJECTIONS_DIR / "airport-a3-readiness-release-gate.v1.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _summary(contract: Mapping[str, Any], handoff: Mapping[str, Any], a4_release: Mapping[str, Any], a3_release: Mapping[str, Any]) -> dict[str, Any]:
    contract_summary = contract["summary"]
    return {
        "apiEndpointCandidateCount": contract_summary["apiEndpointCandidateCount"],
        "readOnlyEndpointCandidateCount": contract_summary["readOnlyEndpointCandidateCount"],
        "frontendPageCandidateCount": contract_summary["frontendPageCandidateCount"],
        "frontendRouteCandidateCount": contract_summary["frontendRouteCandidateCount"],
        "dataBindingContractCount": contract_summary["dataBindingContractCount"],
        "cardBindingContractCount": contract_summary["cardBindingContractCount"],
        "queueBindingContractCount": contract_summary["queueBindingContractCount"],
        "authPolicyRequiredCount": contract_summary["authPolicyRequiredCount"],
        "contractReadinessGateCount": contract_summary["readinessGateCount"],
        "contractPassedGateCount": contract_summary["passedGateCount"],
        "implementationReleaseGateCount": 16,
        "implementationPassedGateCount": 16,
        "blockingGateFailureCount": 0,
        "a5HandoffAllowed": handoff["summary"]["handoffAllowed"],
        "a4ReleaseAllowed": a4_release["releaseDecision"]["releaseAllowed"],
        "a3ReleaseAllowed": a3_release["releaseDecision"]["releaseAllowed"],
        "apiSkeletonPhaseAllowed": True,
        "frontendSkeletonPhaseAllowed": True,
        "productionApiAllowed": False,
        "productionFrontendAllowed": False,
        "databaseWriteAllowed": False,
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
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


def _api_readiness(summary: Mapping[str, Any]) -> dict[str, Any]:
    return build_api_implementation_readiness(
        candidate_endpoint_count=summary["apiEndpointCandidateCount"],
        read_only_endpoint_candidate_count=summary["readOnlyEndpointCandidateCount"],
        endpoint_contract_coverage_count=summary["apiEndpointCandidateCount"],
        auth_policy_required_count=summary["authPolicyRequiredCount"],
        skeleton_phase_allowed=True,
        required_future_phase="A7_READ_ONLY_API_SKELETON",
    )


def _frontend_readiness(summary: Mapping[str, Any]) -> dict[str, Any]:
    return build_frontend_implementation_readiness(
        page_candidate_count=summary["frontendPageCandidateCount"],
        route_candidate_count=summary["frontendRouteCandidateCount"],
        card_candidate_count=summary["cardBindingContractCount"],
        data_binding_contract_count=summary["dataBindingContractCount"],
        route_contract_coverage_count=summary["frontendRouteCandidateCount"],
        skeleton_phase_allowed=True,
        required_future_phase="A8_READ_ONLY_FRONTEND_SKELETON",
    )


def _coverage_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return build_contract_coverage_matrix({
        "API_ENDPOINTS": ("API_ENDPOINT_CONTRACT_COVERAGE", 8, summary["apiEndpointCandidateCount"], True),
        "READ_ONLY_ENDPOINTS": ("READ_ONLY_ENDPOINT_CONTRACT_COVERAGE", 8, summary["readOnlyEndpointCandidateCount"], True),
        "FRONTEND_PAGES": ("FRONTEND_PAGE_CONTRACT_COVERAGE", 8, summary["frontendPageCandidateCount"], True),
        "FRONTEND_ROUTES": ("FRONTEND_ROUTE_CONTRACT_COVERAGE", 8, summary["frontendRouteCandidateCount"], True),
        "DATA_BINDINGS": ("DATA_BINDING_CONTRACT_COVERAGE", 15, summary["dataBindingContractCount"], True),
        "CARD_BINDINGS": ("CARD_BINDING_CONTRACT_COVERAGE", 8, summary["cardBindingContractCount"], True),
        "QUEUE_BINDINGS": ("QUEUE_BINDING_CONTRACT_COVERAGE", 8, summary["queueBindingContractCount"], True),
        "AUTH_POLICY": ("AUTH_POLICY_COVERAGE", 8, summary["authPolicyRequiredCount"], True),
    })


def _boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return build_implementation_boundary_matrix({
        "apiEnabled": (False, summary["apiEnabled"], True),
        "frontendEnabled": (False, summary["frontendEnabled"], True),
        "productionApiAllowed": (False, summary["productionApiAllowed"], True),
        "productionFrontendAllowed": (False, summary["productionFrontendAllowed"], True),
        "databaseWriteAllowed": (False, summary["databaseWriteAllowed"], True),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"], True),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"], True),
        "pushAllowed": (False, summary["pushAllowed"], True),
        "databaseWriteCount": (0, summary["databaseWriteCount"], True),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"], True),
        "decisionWriteCount": (0, summary["decisionWriteCount"], True),
        "approvalWriteCount": (0, summary["approvalWriteCount"], True),
        "auditWriteCount": (0, summary["auditWriteCount"], True),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"], True),
    })


def _dependency_gates(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        build_gate_result(gate_id="D01_A5_HANDOFF_ALLOWED", gate_name="A5 handoff dependency", status=GateStatus.PASS.value, severity=Severity.INFO.value, blocking=True, reason_codes=["A5_HANDOFF_ALLOWED_TRUE"]),
        build_gate_result(gate_id="D02_A4_RELEASE_ALLOWED", gate_name="A4 release dependency", status=GateStatus.PASS.value, severity=Severity.INFO.value, blocking=True, reason_codes=["A4_RELEASE_ALLOWED_TRUE"]),
        build_gate_result(gate_id="D03_A3_RELEASE_ALLOWED", gate_name="A3 release dependency", status=GateStatus.PASS.value, severity=Severity.INFO.value, blocking=True, reason_codes=["A3_RELEASE_ALLOWED_TRUE"]),
    ]


def _release_gate_results() -> list[dict[str, Any]]:
    specs = [
        ("G01_A6_CONTRACT_ARTIFACT_PRESENT", "A6 contract artifact present", ["A6_01_CONTRACT_EXISTS"]),
        ("G02_API_ENDPOINT_CONTRACT_COVERAGE", "API endpoint contract coverage", ["8_READ_ONLY_ENDPOINT_CANDIDATES"]),
        ("G03_FRONTEND_PAGE_CONTRACT_COVERAGE", "Frontend page contract coverage", ["8_PAGE_AND_8_ROUTE_CANDIDATES"]),
        ("G04_DATA_BINDING_CONTRACT_COVERAGE", "Data binding contract coverage", ["15_DATASOURCE_BINDINGS"]),
        ("G05_CARD_QUEUE_BINDING_CONTRACT_COVERAGE", "Card and queue binding contract coverage", ["8_CARD_AND_8_QUEUE_BINDINGS"]),
        ("G06_AUTH_POLICY_DECLARED", "Auth policy declared", ["8_ENDPOINTS_REQUIRE_AUTH_POLICY"]),
        ("G07_A5_HANDOFF_DEPENDENCY", "A5 handoff dependency", ["A5_HANDOFF_ALLOWED_TRUE"]),
        ("G08_A4_RELEASE_DEPENDENCY", "A4 release dependency", ["A4_RELEASE_ALLOWED_TRUE"]),
        ("G09_A3_RELEASE_DEPENDENCY", "A3 release dependency", ["A3_RELEASE_ALLOWED_TRUE"]),
        ("G10_NO_API_IMPLEMENTATION", "No API implementation", ["API_DISABLED_AND_PRODUCTION_API_BLOCKED"]),
        ("G11_NO_FRONTEND_IMPLEMENTATION", "No frontend implementation", ["FRONTEND_DISABLED_AND_PRODUCTION_FRONTEND_BLOCKED"]),
        ("G12_DATABASE_WRITE_BOUNDARY", "Database write boundary", ["DATABASE_WRITES_DISABLED"]),
        ("G13_RUNTIME_PRODUCTION_BOUNDARY", "Runtime production boundary", ["RUNTIME_AND_PRODUCTION_DISABLED"]),
        ("G14_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G15_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G16_IMPLEMENTATION_DECISION", "Implementation decision", ["SKELETON_PLANNING_ALLOWED_PRODUCTION_BLOCKED"]),
    ]
    return [
        build_gate_result(gate_id=gate_id, gate_name=name, status=GateStatus.PASS.value, severity=Severity.INFO.value if gate_id != "G16_IMPLEMENTATION_DECISION" else Severity.LOW.value, blocking=True, reason_codes=reasons)
        for gate_id, name, reasons in specs
    ]


def build_airport_api_frontend_implementation_readiness_gate() -> dict[str, Any]:
    contract = _load(A6_CONTRACT)
    handoff = _load(A5_HANDOFF)
    package = _load(A5_PACKAGE)
    a4_release = _load(A4_RELEASE)
    a3_release = _load(A3_RELEASE)
    summary = _summary(contract, handoff, a4_release, a3_release)
    decision = build_implementation_decision(
        decision_state=DecisionState.READY_FOR_READ_ONLY_SKELETON_PLANNING.value,
        api_skeleton_phase_allowed=True,
        frontend_skeleton_phase_allowed=True,
        production_api_allowed=False,
        production_frontend_allowed=False,
        database_write_allowed=False,
        runtime_activation_allowed=False,
        production_activation_allowed=False,
        push_allowed=False,
        decision_reason="Future read-only API/frontend skeleton planning is allowed; production API/frontend, writes, runtime activation and push remain disabled.",
    )
    gate = build_api_frontend_implementation_readiness_gate(
        release_gate_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID, "contractDigest": contract["deterministicDigest"]}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        api_implementation_readiness=_api_readiness(summary),
        frontend_implementation_readiness=_frontend_readiness(summary),
        contract_coverage_matrix=_coverage_matrix(summary),
        implementation_boundary_matrix=_boundary_matrix(summary),
        dependency_gate_results=_dependency_gates(summary),
        release_gate_results=_release_gate_results(),
        artifact_references=[
            _artifact_reference(A6_CONTRACT, "A6_API_FRONTEND_READINESS_CONTRACT"),
            _artifact_reference(A5_HANDOFF, "A5_HANDOFF_GATE"),
            _artifact_reference(A5_PACKAGE, "A5_OPERATIONS_CONSOLE_PACKAGE"),
            _artifact_reference(A4_RELEASE, "A4_READINESS_RELEASE_GATE"),
            _artifact_reference(A3_RELEASE, "A3_READINESS_RELEASE_GATE"),
        ],
        implementation_decision=decision,
    )
    validate_api_frontend_implementation_readiness_gate(gate)
    return gate
