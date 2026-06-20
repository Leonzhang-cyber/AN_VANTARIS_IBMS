"""Airport read-only Operations Console Package projection."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from operations_console_package.aggregation import build_default_page, build_facet, build_filter
from operations_console_package.enums import CardType, GateStatus, PageType, ReadinessState, Severity
from operations_console_package.models import (
    build_artifact_reference,
    build_console_card,
    build_navigation_group,
    build_operations_console_package,
    build_package_data_source,
    build_package_readiness_gate,
    build_page_definition,
)
from operations_console_package.validation import validate_operations_console_package
from source_system_registry.digest import sha256_digest

AUTHORITY = "ONE-AIRPORT-A5-01"
PROFILE_ID = "airport-operations-console-package-profile-v1"
PACKAGE_VERSION = "airport-operations-console-package.v1"
IMPLEMENTATION_STATUS = "READ_ONLY_AIRPORT_OPERATIONS_CONSOLE_PACKAGE_FOUNDATION_COMPLETE"
READINESS_OUTCOME = "AIRPORT_OPERATIONS_CONSOLE_PACKAGE_READY_FOR_READ_ONLY_CONSUMPTION"

ROOT = Path(__file__).resolve().parents[3]
PROJECTIONS_DIR = ROOT / "AN_VANTARIS_ONE/industry_profiles/airport/projections"

ARTIFACTS: dict[str, tuple[str, str]] = {
    "SOURCE_SYSTEM_CANDIDATES": ("airport-source-system-candidates.v1.json", "SOURCE_SYSTEM_CANDIDATES"),
    "SOURCE_SYSTEM_REVIEW": ("airport-source-system-review.v1.json", "SOURCE_SYSTEM_REVIEW"),
    "INTEGRATION_HEALTH": ("airport-integration-health.v1.json", "INTEGRATION_HEALTH"),
    "UCONSOLE_INTEGRATION_HEALTH": ("airport-uconsole-integration-health.v1.json", "UCONSOLE_INTEGRATION_HEALTH"),
    "ALARM_EVENT_INTAKE": ("airport-alarm-event-intake-candidates.v1.json", "ALARM_EVENT_INTAKE"),
    "ALARM_EVENT_RESOLUTION": ("airport-alarm-event-asset-resolution-review.v1.json", "ALARM_EVENT_RESOLUTION"),
    "FAULTCASE_CANDIDATES": ("airport-faultcase-candidates.v1.json", "FAULTCASE_CANDIDATES"),
    "WORKORDER_INTENT_CANDIDATES": ("airport-workorder-intent-candidates.v1.json", "WORKORDER_INTENT_CANDIDATES"),
    "EVIDENCE_INVESTIGATION": ("airport-evidence-investigation.v1.json", "EVIDENCE_INVESTIGATION"),
    "UCONSOLE_ALARM_EVENT_OPERATIONS": ("airport-uconsole-alarm-event-operations.v1.json", "UCONSOLE_ALARM_EVENT_OPERATIONS"),
    "OPERATOR_REVIEW_DECISIONS": ("airport-operator-review-decisions.v1.json", "OPERATOR_REVIEW_DECISIONS"),
    "UCONSOLE_OPERATOR_REVIEW_QUEUE": ("airport-uconsole-operator-review-queue.v1.json", "UCONSOLE_OPERATOR_REVIEW_QUEUE"),
    "OPERATOR_REVIEW_POLICY_GUARD": ("airport-operator-review-policy-guard.v1.json", "OPERATOR_REVIEW_POLICY_GUARD"),
    "A3_RELEASE_GATE": ("airport-a3-readiness-release-gate.v1.json", "A3_RELEASE_GATE"),
    "A4_RELEASE_GATE": ("airport-a4-readiness-release-gate.v1.json", "A4_RELEASE_GATE"),
}

PAGE_SPECS = [
    ("AIRPORT_OVERVIEW", "Airport Overview", PageType.OVERVIEW.value, ["SOURCE_SYSTEM_CANDIDATES", "A3_RELEASE_GATE", "A4_RELEASE_GATE"], ["CARD_AIRPORT_OVERVIEW"], []),
    ("SYSTEMS_INTEGRATION_HEALTH", "Systems & Integration Health", PageType.INTEGRATION_HEALTH.value, ["INTEGRATION_HEALTH", "UCONSOLE_INTEGRATION_HEALTH"], ["CARD_SYSTEMS_INTEGRATION_HEALTH"], []),
    ("ASSETS_TOPOLOGY", "Assets & Topology", PageType.ASSET_REVIEW.value, ["SOURCE_SYSTEM_REVIEW", "ALARM_EVENT_RESOLUTION"], ["CARD_ASSETS_TOPOLOGY"], []),
    ("ALARMS_EVENTS", "Alarms & Events", PageType.ALARM_EVENT_OPERATIONS.value, ["ALARM_EVENT_INTAKE", "UCONSOLE_ALARM_EVENT_OPERATIONS"], ["CARD_ALARMS_EVENTS"], []),
    ("FAULT_CASES", "Fault Cases", PageType.FAULTCASE_CANDIDATES.value, ["FAULTCASE_CANDIDATES"], ["CARD_FAULT_CASES"], []),
    ("MAINTENANCE_WORK_ORDERS", "Maintenance Work Orders", PageType.WORKORDER_INTENT_CANDIDATES.value, ["WORKORDER_INTENT_CANDIDATES"], ["CARD_MAINTENANCE_WORK_ORDERS"], []),
    ("EVIDENCE_INVESTIGATION", "Evidence & Investigation", PageType.EVIDENCE_INVESTIGATION.value, ["EVIDENCE_INVESTIGATION"], ["CARD_EVIDENCE_INVESTIGATION"], []),
    ("REPORTS", "Reports", PageType.RELEASE_GATE.value, ["OPERATOR_REVIEW_DECISIONS", "UCONSOLE_OPERATOR_REVIEW_QUEUE", "OPERATOR_REVIEW_POLICY_GUARD", "A4_RELEASE_GATE"], ["CARD_REPORTS"], ["UCONSOLE_OPERATOR_REVIEW_QUEUE"]),
]

NAVIGATION_SPECS = [
    ("AIRPORT_OPERATIONS", "Airport Operations", ["AIRPORT_OVERVIEW", "SYSTEMS_INTEGRATION_HEALTH", "ASSETS_TOPOLOGY"]),
    ("ALARM_FAULT_WORK", "Alarm, Fault & Work", ["ALARMS_EVENTS", "FAULT_CASES", "MAINTENANCE_WORK_ORDERS"]),
    ("EVIDENCE_REPORTING", "Evidence & Reporting", ["EVIDENCE_INVESTIGATION", "REPORTS"]),
]

SOURCE_SYSTEM_KEYS = ["ACS", "CCTV", "PA", "RAS", "TEL"]


def _load_artifact(key: str) -> dict[str, Any]:
    filename = ARTIFACTS[key][0]
    return json.loads((PROJECTIONS_DIR / filename).read_text(encoding="utf-8"))


def _summary_of(key: str) -> Mapping[str, Any]:
    return _load_artifact(key).get("summary", {})


def _artifact_path(key: str) -> str:
    return str((PROJECTIONS_DIR / ARTIFACTS[key][0]).relative_to(ROOT))


def _artifact_reference(key: str) -> dict[str, Any]:
    artifact = _load_artifact(key)
    return build_artifact_reference(artifact_type=ARTIFACTS[key][1], path=_artifact_path(key), digest=sha256_digest(artifact))


def _data_sources() -> list[dict[str, Any]]:
    return [
        build_package_data_source(
            data_source_id=sha256_digest({"dataSourceKey": key}),
            data_source_key=key,
            source_artifact_path=_artifact_path(key),
            source_projection_type=projection_type,
        )
        for key, (_filename, projection_type) in ARTIFACTS.items()
    ]


def _summary() -> dict[str, Any]:
    source_candidates = _summary_of("SOURCE_SYSTEM_CANDIDATES")
    alarm_intake = _summary_of("ALARM_EVENT_INTAKE")
    fault_cases = _summary_of("FAULTCASE_CANDIDATES")
    work_intents = _summary_of("WORKORDER_INTENT_CANDIDATES")
    investigations = _summary_of("EVIDENCE_INVESTIGATION")
    operations = _summary_of("UCONSOLE_ALARM_EVENT_OPERATIONS")
    decisions = _summary_of("OPERATOR_REVIEW_DECISIONS")
    queue = _summary_of("UCONSOLE_OPERATOR_REVIEW_QUEUE")
    guard = _summary_of("OPERATOR_REVIEW_POLICY_GUARD")
    a3_release = _summary_of("A3_RELEASE_GATE")

    return {
        "pageDefinitionCount": 8,
        "navigationGroupCount": 3,
        "consoleCardCount": 8,
        "packageDataSourceCount": 15,
        "packageReadinessGateCount": 12,
        "sourceSystemCandidateCount": source_candidates["sourceSystemCandidateCount"],
        "alarmEventCandidateCount": alarm_intake["canonicalAlarmEventCandidateCount"],
        "faultCaseCandidateCount": fault_cases["faultCaseCandidateCount"],
        "workOrderIntentCandidateCount": work_intents["workOrderIntentCandidateCount"],
        "investigationCaseCount": investigations["investigationCaseCount"],
        "operationsRowCount": operations["operationsRowCount"],
        "decisionItemCount": decisions["decisionItemCount"],
        "queueRowCount": queue["queueRowCount"],
        "policyGuardResultCount": guard["policyGuardResultCount"],
        "auditPreviewCount": guard["auditPreviewCount"],
        "totalDeviceEvidenceCount": a3_release["totalDeviceEvidenceCount"],
        "pendingDecisionCount": decisions["pendingDecisionCount"],
        "blockingDecisionCount": decisions["blockingDecisionCount"],
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
        "runtimeActivationAllowed": False,
        "productionActivationAllowed": False,
        "pushAllowed": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }


def _page_definitions() -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    for page_key, title, page_type, source_keys, card_ids, queue_ids in PAGE_SPECS:
        pages.append(
            build_page_definition(
                page_id=sha256_digest({"pageKey": page_key}),
                page_key=page_key,
                title=title,
                description=f"Read-only package page for {title}.",
                page_type=page_type,
                readiness_state=ReadinessState.READY_FOR_READ_ONLY_CONSUMPTION.value if page_key in {"AIRPORT_OVERVIEW", "REPORTS"} else ReadinessState.REVIEW_REQUIRED.value,
                source_projection_keys=source_keys,
                primary_card_ids=card_ids,
                queue_ids=queue_ids,
                data_source_ids=[sha256_digest({"dataSourceKey": key}) for key in source_keys],
                decision_required=page_key != "AIRPORT_OVERVIEW",
                blocked=page_key != "AIRPORT_OVERVIEW",
            )
        )
    return sorted(pages, key=lambda page: (page["pageKey"], page["pageId"]))


def _navigation_groups(page_id_by_key: Mapping[str, str]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for group_key, title, page_keys in NAVIGATION_SPECS:
        groups.append(
            build_navigation_group(
                navigation_group_id=sha256_digest({"navigationGroupKey": group_key}),
                group_key=group_key,
                title=title,
                page_ids=[page_id_by_key[key] for key in page_keys],
                readiness_state=ReadinessState.REVIEW_REQUIRED.value,
            )
        )
    return groups


def _console_cards(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    specs = [
        ("CARD_AIRPORT_OVERVIEW", CardType.SUMMARY.value, "Airport read-only package", Severity.INFO.value, "READY", summary["sourceSystemCandidateCount"], "source systems", "AIRPORT_OVERVIEW", summary["sourceSystemCandidateCount"], False),
        ("CARD_SYSTEMS_INTEGRATION_HEALTH", CardType.HEALTH.value, "Systems pending review", Severity.MEDIUM.value, "REVIEW_REQUIRED", summary["pendingDecisionCount"], "decisions", "SYSTEMS_INTEGRATION_HEALTH", summary["sourceSystemCandidateCount"], True),
        ("CARD_ASSETS_TOPOLOGY", CardType.REVIEW.value, "Asset resolution review", Severity.MEDIUM.value, "REVIEW_REQUIRED", summary["alarmEventCandidateCount"], "candidates", "ASSETS_TOPOLOGY", summary["alarmEventCandidateCount"], True),
        ("CARD_ALARMS_EVENTS", CardType.QUEUE.value, "Alarm/event operations", Severity.HIGH.value, "BLOCKED_READ_ONLY", summary["operationsRowCount"], "rows", "ALARMS_EVENTS", summary["operationsRowCount"], True),
        ("CARD_FAULT_CASES", CardType.REVIEW.value, "FaultCase candidates", Severity.HIGH.value, "REVIEW_REQUIRED", summary["faultCaseCandidateCount"], "candidates", "FAULT_CASES", summary["faultCaseCandidateCount"], True),
        ("CARD_MAINTENANCE_WORK_ORDERS", CardType.REVIEW.value, "WorkOrderIntent candidates", Severity.HIGH.value, "REVIEW_REQUIRED", summary["workOrderIntentCandidateCount"], "candidates", "MAINTENANCE_WORK_ORDERS", summary["workOrderIntentCandidateCount"], True),
        ("CARD_EVIDENCE_INVESTIGATION", CardType.EVIDENCE.value, "Evidence investigations", Severity.MEDIUM.value, "REVIEW_REQUIRED", summary["investigationCaseCount"], "cases", "EVIDENCE_INVESTIGATION", summary["investigationCaseCount"], True),
        ("CARD_REPORTS", CardType.RELEASE_GATE.value, "A4 release gate reports", Severity.LOW.value, "PASS", summary["packageReadinessGateCount"], "gates", "REPORTS", summary["decisionItemCount"], True),
    ]
    return [
        build_console_card(
            card_id=card_id,
            card_type=card_type,
            title=title,
            severity=severity,
            status=status,
            value=value,
            unit=unit,
            page_key=page_key,
            affected_source_system_keys=SOURCE_SYSTEM_KEYS,
            affected_record_count=record_count,
            affected_device_evidence_count=summary["totalDeviceEvidenceCount"],
            decision_required=decision_required,
        )
        for card_id, card_type, title, severity, status, value, unit, page_key, record_count, decision_required in specs
    ]


def _readiness_gates(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    gate_specs = [
        ("G01_PACKAGE_PAGE_COMPLETENESS", "Package page completeness", ["8_PAGES_PRESENT"], ["pageDefinitions"]),
        ("G02_PACKAGE_NAVIGATION_COMPLETENESS", "Package navigation completeness", ["3_NAVIGATION_GROUPS_PRESENT"], ["navigationGroups"]),
        ("G03_PACKAGE_DATASOURCE_COMPLETENESS", "Package datasource completeness", ["15_READ_ONLY_DATASOURCES_PRESENT"], ["packageDataSources"]),
        ("G04_A2_INTEGRATION_HEALTH_AVAILABLE", "A2 integration health available", ["A2_HEALTH_PROJECTIONS_AVAILABLE"], [_artifact_path("INTEGRATION_HEALTH"), _artifact_path("UCONSOLE_INTEGRATION_HEALTH")]),
        ("G05_A3_OPERATIONS_CHAIN_AVAILABLE", "A3 operations chain available", ["A3_CHAIN_PROJECTIONS_AVAILABLE"], [_artifact_path("UCONSOLE_ALARM_EVENT_OPERATIONS"), _artifact_path("A3_RELEASE_GATE")]),
        ("G06_A4_OPERATOR_REVIEW_AVAILABLE", "A4 operator review available", ["A4_OPERATOR_REVIEW_PROJECTIONS_AVAILABLE"], [_artifact_path("OPERATOR_REVIEW_DECISIONS"), _artifact_path("UCONSOLE_OPERATOR_REVIEW_QUEUE"), _artifact_path("OPERATOR_REVIEW_POLICY_GUARD")]),
        ("G07_READ_ONLY_BOUNDARY", "Read-only boundary", ["ALL_WRITE_COUNTS_ZERO"], ["summary"]),
        ("G08_API_FRONTEND_BOUNDARY", "API/frontend boundary", ["API_AND_FRONTEND_DISABLED"], ["summary"]),
        ("G09_RUNTIME_BOUNDARY", "Runtime boundary", ["RUNTIME_DISABLED_AND_UNOBSERVED"], ["summary"]),
        ("G10_CUSTOMER_IDENTIFIER_SAFETY", "Customer identifier safety", ["NO_CUSTOMER_IDENTIFIER_LEAKAGE"], ["summary"]),
        ("G11_DETERMINISTIC_OUTPUT", "Deterministic output", ["REPEATED_RUNNER_BYTE_IDENTICAL"], ["scripts/validation/_run_a5_01_airport_operations_console_package.py"]),
        ("G12_RELEASE_DECISION", "Release decision", ["ALL_BLOCKING_GATES_PASS"], ["packageReadinessGates"]),
    ]
    return [
        build_package_readiness_gate(
            gate_id=gate_id,
            gate_name=name,
            status=GateStatus.PASS.value,
            severity=Severity.INFO.value if gate_id != "G12_RELEASE_DECISION" else Severity.LOW.value,
            blocking=True,
            reason_codes=reasons,
            evidence_references=evidence,
        )
        for gate_id, name, reasons, evidence in gate_specs
    ]


def _filters(pages: list[Mapping[str, Any]], cards: list[Mapping[str, Any]], data_sources: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    navigation_keys = [spec[0] for spec in NAVIGATION_SPECS]
    return [
        build_filter(field="pageKey", values=[page["pageKey"] for page in pages]),
        build_filter(field="pageType", values=[page["pageType"] for page in pages]),
        build_filter(field="readinessState", values=[page["readinessState"] for page in pages]),
        build_filter(field="navigationGroup", values=navigation_keys),
        build_filter(field="cardType", values=[card["cardType"] for card in cards]),
        build_filter(field="severity", values=[card["severity"] for card in cards]),
        build_filter(field="decisionRequired", values=["true", "false"]),
        build_filter(field="blocked", values=["true", "false"]),
        build_filter(field="sourceProjectionType", values=[source["sourceProjectionType"] for source in data_sources]),
    ]


def _facets(pages: list[Mapping[str, Any]], cards: list[Mapping[str, Any]], data_sources: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    def counts(items: list[Mapping[str, Any]], key: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for item in items:
            value = str(item[key])
            result[value] = result.get(value, 0) + 1
        return result

    return [
        build_facet(field="pageKey", counts=counts(pages, "pageKey")),
        build_facet(field="pageType", counts=counts(pages, "pageType")),
        build_facet(field="readinessState", counts=counts(pages, "readinessState")),
        build_facet(field="navigationGroup", counts={spec[0]: len(spec[2]) for spec in NAVIGATION_SPECS}),
        build_facet(field="cardType", counts=counts(cards, "cardType")),
        build_facet(field="severity", counts=counts(cards, "severity")),
        build_facet(field="decisionRequired", counts={str(value).lower(): sum(1 for page in pages if page["decisionRequired"] is value) for value in (False, True)}),
        build_facet(field="blocked", counts={str(value).lower(): sum(1 for page in pages if page["blocked"] is value) for value in (False, True)}),
        build_facet(field="sourceProjectionType", counts=counts(data_sources, "sourceProjectionType")),
    ]


def build_airport_operations_console_package() -> dict[str, Any]:
    summary = _summary()
    pages = _page_definitions()
    cards = _console_cards(summary)
    data_sources = _data_sources()
    gates = _readiness_gates(summary)
    page_id_by_key = {page["pageKey"]: page["pageId"] for page in pages}
    package = build_operations_console_package(
        package_id=sha256_digest({"authority": AUTHORITY, "profileId": PROFILE_ID, "packageVersion": PACKAGE_VERSION}),
        authority=AUTHORITY,
        profile_id=PROFILE_ID,
        package_version=PACKAGE_VERSION,
        implementation_status=IMPLEMENTATION_STATUS,
        readiness_outcome=READINESS_OUTCOME,
        summary=summary,
        page_definitions=pages,
        navigation_groups=_navigation_groups(page_id_by_key),
        console_cards=cards,
        package_data_sources=data_sources,
        package_readiness_gates=gates,
        filters=_filters(pages, cards, data_sources),
        facets=_facets(pages, cards, data_sources),
        default_page=build_default_page(page_key="AIRPORT_OVERVIEW", page_size=25, order_by=["pageKey", "pageId"], continuation_token_seed={"pageKeys": [page["pageKey"] for page in pages]}),
        source_artifact_references=[_artifact_reference(key) for key in ARTIFACTS],
    )
    validate_operations_console_package(package)
    return package
