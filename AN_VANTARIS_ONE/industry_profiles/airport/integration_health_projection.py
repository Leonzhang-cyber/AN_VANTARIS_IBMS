"""Airport consumer projection for the generic Integration Health read model."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from integration_health.evaluation import evaluate_static_binding
from integration_health.projection import (
    build_facets,
    paginate_health_records,
    sort_health_records,
)
from source_system_registry.digest import sha256_digest
from source_system_registry.errors import SourceSystemRegistryError

from .candidate_projection import run_airport_source_system_projection
from .source_system_review_projection import (
    compare_deterministic_outputs,
    run_airport_source_system_review_projection,
)

AUTHORITY = "ONE-AIRPORT-A2-03"
IMPLEMENTATION_STATUS = "GENERIC_INTEGRATION_HEALTH_READ_MODEL_COMPLETE"
READINESS_OUTCOME = "INTEGRATION_HEALTH_DECLARATION_COMPLETE_RUNTIME_EVIDENCE_PENDING"


def _build_filters() -> list[dict[str, Any]]:
    return [
        {"filterKey": "sourceSystemKey", "filterType": "ENUM", "options": ["ACS", "CCTV", "PA", "RAS", "TEL"]},
        {
            "filterKey": "healthState",
            "filterType": "ENUM",
            "options": ["UNKNOWN", "NOT_APPLICABLE", "REVIEW_REQUIRED"],
        },
        {
            "filterKey": "readinessState",
            "filterType": "ENUM",
            "options": ["REVIEW_REQUIRED", "RUNTIME_VERIFICATION_REQUIRED"],
        },
        {"filterKey": "severity", "filterType": "ENUM", "options": ["INFO", "LOW", "MEDIUM"]},
        {"filterKey": "approvalState", "filterType": "ENUM", "options": ["DRAFT", "REVIEW_REQUIRED"]},
        {"filterKey": "lifecycleState", "filterType": "ENUM", "options": ["CANDIDATE"]},
        {"filterKey": "runtimeObserved", "filterType": "BOOLEAN", "options": ["false"]},
        {"filterKey": "reviewRequired", "filterType": "BOOLEAN", "options": ["true", "false"]},
        {
            "filterKey": "findingType",
            "filterType": "ENUM",
            "options": [
                "ALIAS_APPROVAL_PENDING",
                "CONNECTOR_REFERENCE_UNDECLARED",
                "EDGE_GATEWAY_REFERENCE_UNDECLARED",
                "HEALTH_POLICY_NOT_EVALUATED",
                "LINK_ROUTE_REFERENCE_UNDECLARED",
                "NAMESPACE_INTERPRETATION_PENDING",
                "REGISTRY_APPROVAL_PENDING",
                "RUNTIME_EVIDENCE_UNAVAILABLE",
            ],
        },
    ]


def build_airport_integration_health_projection(
    source_system_review: Mapping[str, Any],
    *,
    candidates: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    bindings = list(source_system_review.get("evidenceBindings", []))
    if len(bindings) != 5:
        raise SourceSystemRegistryError(
            "INTEGRATION_HEALTH_BINDING_COUNT_MISMATCH",
            "expected exactly five evidence bindings",
        )

    candidate_by_key = {
        str(item["sourceSystemKey"]): item
        for item in (candidates or {}).get("candidates", [])
    }

    records = sort_health_records(
        [
            evaluate_static_binding(
                binding,
                candidate=candidate_by_key.get(str(binding["sourceSystemKey"])),
            )
            for binding in bindings
        ]
    )
    total_evidence = sum(int(item["deviceEvidenceCount"]) for item in records)
    if total_evidence != 470:
        raise SourceSystemRegistryError(
            "INTEGRATION_HEALTH_EVIDENCE_COUNT_MISMATCH",
            f"expected 470 evidence records, got {total_evidence}",
        )

    findings = sorted(
        [finding for record in records for finding in record["findings"]],
        key=lambda item: (item["findingType"], item["findingId"]),
    )

    summary = {
        "integrationHealthRecordCount": len(records),
        "runtimeObservedSystemCount": 0,
        "runtimeVerifiedSystemCount": 0,
        "healthySystemCount": 0,
        "activeSystemCount": sum(1 for item in records if item["lifecycleState"] == "ACTIVE"),
        "registeredSystemCount": sum(1 for item in records if item["lifecycleState"] == "REGISTERED"),
        "approvedSystemCount": sum(1 for item in records if item["approvalState"] == "APPROVED"),
        "registryApprovalPendingCount": sum(
            1 for item in findings if item["findingType"] == "REGISTRY_APPROVAL_PENDING"
        ),
        "aliasApprovalPendingCount": sum(
            1 for item in findings if item["findingType"] == "ALIAS_APPROVAL_PENDING"
        ),
        "namespaceReviewPendingCount": sum(
            1 for item in findings if item["findingType"] == "NAMESPACE_INTERPRETATION_PENDING"
        ),
        "runtimeVerificationRequiredCount": sum(
            1
            for item in records
            if not item["runtimeObservationHealth"]["runtimeObserved"]
        ),
        "totalEvidenceDeviceCount": total_evidence,
        "runtimeConnectorExecutionEnabled": False,
        "databaseAccessEnabled": False,
        "productionActivationEnabled": False,
        "containsCustomerAssetIdentifiers": False,
        "crossIndustry": True,
        "airportSpecific": False,
    }

    projection = {
        "authority": AUTHORITY,
        "implementationStatus": IMPLEMENTATION_STATUS,
        "readinessOutcome": READINESS_OUTCOME,
        "summary": summary,
        "healthRecords": records,
        "findings": findings,
        "filters": _build_filters(),
        "facets": build_facets(records),
        "defaultPage": paginate_health_records(records, page_size=25),
    }
    projection["resultDigest"] = sha256_digest({k: v for k, v in projection.items() if k != "resultDigest"})
    return projection


def run_airport_integration_health_projection(
    *,
    evidence_dir: Path,
    profile_path: Path,
    output_path: Path | None = None,
) -> dict[str, Any]:
    review = run_airport_source_system_review_projection(
        evidence_dir=evidence_dir,
        profile_path=profile_path,
        output_path=None,
    )
    candidates = run_airport_source_system_projection(
        evidence_dir=evidence_dir,
        profile_path=profile_path,
        output_path=None,
    )
    projection = build_airport_integration_health_projection(review, candidates=candidates)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return projection


__all__ = [
    "build_airport_integration_health_projection",
    "compare_deterministic_outputs",
    "run_airport_integration_health_projection",
]
