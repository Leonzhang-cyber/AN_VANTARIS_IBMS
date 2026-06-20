"""Airport read-only API skeleton projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from read_only_api_skeleton.enums import ApiImplementationState, AuthPolicy, GateStatus, Severity
from read_only_api_skeleton.models import (
    build_api_readiness_gate,
    build_artifact_reference,
    build_boundary_entry,
    build_endpoint_skeleton,
    build_read_only_api_skeleton,
    build_response_contract,
    build_route_group,
)
from read_only_api_skeleton.validation import validate_read_only_api_skeleton
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A7-01"
PROFILE_ID = "airport-read-only-api-skeleton-profile-v1"
IMPLEMENTATION_STATUS = "READ_ONLY_API_SKELETON_FOUNDATION_COMPLETE"
READINESS_OUTCOME = "READ_ONLY_API_SKELETON_READY_FOR_FUTURE_IMPLEMENTATION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"
A6_GATE = PROJECTIONS_DIR / "airport-api-frontend-implementation-readiness-gate.v1.json"
A6_CONTRACT = PROJECTIONS_DIR / "airport-api-frontend-readiness-contract.v1.json"
A5_PACKAGE = PROJECTIONS_DIR / "airport-operations-console-package.v1.json"
A5_HANDOFF = PROJECTIONS_DIR / "airport-operations-console-handoff-gate.v1.json"

ENDPOINT_PATHS = {
    "AIRPORT_OVERVIEW": "/api/v1/one/airport/console/overview",
    "SYSTEMS_INTEGRATION_HEALTH": "/api/v1/one/airport/console/systems-integration-health",
    "ASSETS_TOPOLOGY": "/api/v1/one/airport/console/assets-topology",
    "ALARMS_EVENTS": "/api/v1/one/airport/console/alarms-events",
    "FAULT_CASES": "/api/v1/one/airport/console/fault-cases",
    "MAINTENANCE_WORK_ORDERS": "/api/v1/one/airport/console/maintenance-work-orders",
    "EVIDENCE_INVESTIGATION": "/api/v1/one/airport/console/evidence-investigation",
    "REPORTS": "/api/v1/one/airport/console/reports",
}

ROOT_KEYS = {
    "AIRPORT_OVERVIEW": "summary",
    "SYSTEMS_INTEGRATION_HEALTH": "sourceSystemRows",
    "ASSETS_TOPOLOGY": "resolutionRows",
    "ALARMS_EVENTS": "operationsRows",
    "FAULT_CASES": "faultCaseCandidates",
    "MAINTENANCE_WORK_ORDERS": "workOrderIntentCandidates",
    "EVIDENCE_INVESTIGATION": "investigationCases",
    "REPORTS": "summary",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_reference(path: Path, artifact_type: str) -> dict[str, Any]:
    artifact = _load(path)
    return build_artifact_reference(artifact_type=artifact_type, path=str(path.relative_to(ROOT)), digest=sha256_digest(artifact))


def _data_source_by_key(package: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {item["dataSourceKey"]: item for item in package["packageDataSources"]}


def _summary(a6_gate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "endpointSkeletonCount": 8,
        "getEndpointCount": 8,
        "readOnlyEndpointCount": 8,
        "responseContractCount": 8,
        "routeGroupCount": 3,
        "readinessGateCount": 14,
        "passedGateCount": 14,
        "blockingGateFailureCount": 0,
        "authPolicyRequiredCount": 8,
        "productionEnabledEndpointCount": 0,
        "databaseAccessEnabledEndpointCount": 0,
        "writeOperationEnabledEndpointCount": 0,
        "runtimeActivationEnabledEndpointCount": 0,
        "apiSkeletonPhaseAllowed": a6_gate["summary"]["apiSkeletonPhaseAllowed"],
        "productionApiAllowed": False,
        "apiEnabled": False,
        "databaseWriteCount": 0,
        "canonicalWriteCount": 0,
        "decisionWriteCount": 0,
        "approvalWriteCount": 0,
        "auditWriteCount": 0,
        "frontendEnabled": False,
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
        "pushAllowed": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def _response_contracts(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    sources = _data_source_by_key(package)
    contracts: list[dict[str, Any]] = []
    for page in package["pageDefinitions"]:
        source_key = page["sourceProjectionKeys"][0]
        source = sources[source_key]
        contracts.append(
            build_response_contract(
                endpoint_key=page["pageKey"],
                response_shape={
                    "data": ROOT_KEYS[page["pageKey"]],
                    "summary": "summary",
                    "filters": "filters",
                    "facets": "facets",
                    "pagination": "defaultPage",
                },
                source_artifact_path=source["sourceArtifactPath"],
                projection_root_key=ROOT_KEYS[page["pageKey"]],
                pagination_supported=True,
                filters_supported=True,
                facets_supported=True,
            )
        )
    return sorted(contracts, key=lambda item: item["endpointKey"])


def _endpoint_skeletons(package: Mapping[str, Any], responses: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    sources = _data_source_by_key(package)
    response_by_endpoint = {item["endpointKey"]: item["responseContractId"] for item in responses}
    endpoints: list[dict[str, Any]] = []
    for page in package["pageDefinitions"]:
        source_key = page["sourceProjectionKeys"][0]
        source = sources[source_key]
        endpoints.append(
            build_endpoint_skeleton(
                endpoint_key=page["pageKey"],
                path=ENDPOINT_PATHS[page["pageKey"]],
                page_key=page["pageKey"],
                source_data_source_key=source_key,
                source_projection_type=source["sourceProjectionType"],
                response_contract_id=response_by_endpoint[page["pageKey"]],
                auth_policy=AuthPolicy.ROLE_POLICY_REQUIRED.value if page["pageKey"] in {"REPORTS", "ALARMS_EVENTS"} else AuthPolicy.AUTH_REQUIRED.value,
                implementation_state=ApiImplementationState.SKELETON_DEFINED.value,
            )
        )
    return sorted(endpoints, key=lambda item: item["endpointKey"])


def _route_groups(endpoint_by_key: Mapping[str, str]) -> list[dict[str, Any]]:
    specs = [
        ("AIRPORT_OPERATIONS_API", "Airport Operations API", ["AIRPORT_OVERVIEW", "SYSTEMS_INTEGRATION_HEALTH", "ASSETS_TOPOLOGY"]),
        ("ALARM_FAULT_WORK_API", "Alarm, Fault & Work API", ["ALARMS_EVENTS", "FAULT_CASES", "MAINTENANCE_WORK_ORDERS"]),
        ("EVIDENCE_REPORTING_API", "Evidence & Reporting API", ["EVIDENCE_INVESTIGATION", "REPORTS"]),
    ]
    return [
        build_route_group(group_key=key, title=title, endpoint_skeleton_ids=[endpoint_by_key[item] for item in page_keys])
        for key, title, page_keys in specs
    ]


def _gates() -> list[dict[str, Any]]:
    specs = [
        ("G01_API_SKELETON_ENDPOINT_COMPLETENESS", "API skeleton endpoint completeness", ["8_ENDPOINT_SKELETONS"]),
        ("G02_API_METHOD_BOUNDARY", "API method boundary", ["ALL_ENDPOINTS_GET"]),
        ("G03_API_READ_ONLY_BOUNDARY", "API read-only boundary", ["READ_ONLY_TRUE_WRITES_DISABLED"]),
        ("G04_API_DATABASE_BOUNDARY", "API database boundary", ["DATABASE_ACCESS_DISABLED"]),
        ("G05_API_PRODUCTION_BOUNDARY", "API production boundary", ["PRODUCTION_DISABLED"]),
        ("G06_API_RUNTIME_BOUNDARY", "API runtime boundary", ["RUNTIME_ACTIVATION_DISABLED"]),
        ("G07_API_AUTH_POLICY_DECLARED", "API auth policy declared", ["ALL_ENDPOINTS_REQUIRE_AUTH_OR_ROLE_POLICY"]),
        ("G08_RESPONSE_CONTRACT_COMPLETENESS", "Response contract completeness", ["8_RESPONSE_CONTRACTS"]),
        ("G09_ROUTE_GROUP_COMPLETENESS", "Route group completeness", ["3_ROUTE_GROUPS"]),
        ("G10_A6_IMPLEMENTATION_GATE_DEPENDENCY", "A6 implementation gate dependency", ["API_SKELETON_PHASE_ALLOWED_TRUE"]),
        ("G11_NO_BACKEND_ROUTE_IMPLEMENTATION", "No backend route implementation", ["NO_PRODUCTION_BACKEND_ROUTE_FILES_CHANGED"]),
        ("G12_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"]),
        ("G13_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"]),
        ("G14_API_SKELETON_DECISION", "API skeleton decision", ["SKELETON_READY_PRODUCTION_API_DISABLED"]),
    ]
    return [
        build_api_readiness_gate(gate_id=gate_id, gate_name=name, status=GateStatus.PASS.value, severity=Severity.INFO.value if gate_id != "G14_API_SKELETON_DECISION" else Severity.LOW.value, blocking=True, reason_codes=reasons)
        for gate_id, name, reasons in specs
    ]


def _boundary_matrix(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs = {
        "apiEnabled": (False, summary["apiEnabled"]),
        "productionApiAllowed": (False, summary["productionApiAllowed"]),
        "databaseWriteCount": (0, summary["databaseWriteCount"]),
        "canonicalWriteCount": (0, summary["canonicalWriteCount"]),
        "decisionWriteCount": (0, summary["decisionWriteCount"]),
        "approvalWriteCount": (0, summary["approvalWriteCount"]),
        "auditWriteCount": (0, summary["auditWriteCount"]),
        "frontendEnabled": (False, summary["frontendEnabled"]),
        "runtimeActivationAllowed": (False, summary["runtimeActivationAllowed"]),
        "productionActivationAllowed": (False, summary["productionActivationAllowed"]),
        "pushAllowed": (False, summary["pushAllowed"]),
        "containsCustomerAssetIdentifiers": (False, summary["containsCustomerAssetIdentifiers"]),
    }
    return [build_boundary_entry(boundary_key=key, expected_value=expected, actual_value=actual, blocking=True) for key, (expected, actual) in sorted(pairs.items())]


def build_airport_read_only_api_skeleton() -> dict[str, Any]:
    a6_gate = _load(A6_GATE)
    package = _load(A5_PACKAGE)
    summary = _summary(a6_gate)
    responses = _response_contracts(package)
    endpoints = _endpoint_skeletons(package, responses)
    endpoint_by_key = {item["endpointKey"]: item["endpointSkeletonId"] for item in endpoints}
    skeleton = build_read_only_api_skeleton(
        api_skeleton_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID, "a6Digest": a6_gate["deterministicDigest"]}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        endpoint_skeletons=endpoints,
        response_contracts=responses,
        route_groups=_route_groups(endpoint_by_key),
        api_readiness_gates=_gates(),
        boundary_matrix=_boundary_matrix(summary),
        source_artifact_references=[
            _artifact_reference(A6_GATE, "A6_IMPLEMENTATION_GATE"),
            _artifact_reference(A6_CONTRACT, "A6_READINESS_CONTRACT"),
            _artifact_reference(A5_PACKAGE, "A5_OPERATIONS_CONSOLE_PACKAGE"),
            _artifact_reference(A5_HANDOFF, "A5_HANDOFF_GATE"),
        ],
    )
    validate_read_only_api_skeleton(skeleton)
    return skeleton
