"""Generic static-evidence Integration Health evaluation."""
from __future__ import annotations

from typing import Any, Mapping

from source_system_registry.digest import sha256_digest

from .enums import FindingSeverity, HealthState, ReadinessState
from .models import build_finding, build_health_dimension
from .validation import validate_health_record


def _append_declaration_reference_findings(
    findings: list[dict[str, Any]],
    *,
    source_key: str,
    candidate: Mapping[str, Any],
    evidence_references: list[Mapping[str, Any]],
) -> None:
    declarations = list(candidate.get("integrationDeclarations", []))
    if not declarations:
        return
    declaration = declarations[0]
    reference_checks = (
        ("CONNECTOR_REFERENCE_UNDECLARED", "connectorReference", "Connector reference undeclared"),
        ("EDGE_GATEWAY_REFERENCE_UNDECLARED", "edgeGatewayReference", "EDGE gateway reference undeclared"),
        ("LINK_ROUTE_REFERENCE_UNDECLARED", "linkRouteReference", "LINK route reference undeclared"),
    )
    for finding_type, field, title in reference_checks:
        if declaration.get(field):
            continue
        findings.append(
            build_finding(
                finding_type=finding_type,
                severity=FindingSeverity.INFO,
                reason_code=finding_type,
                title=f"{title} for {source_key}",
                description="Declaration metadata is present without a runtime reference assignment.",
                affected_dimension="declarationHealth",
                decision_required=False,
                affected_source_system_keys=[source_key],
                evidence_references=evidence_references,
            )
        )

    findings.append(
        build_finding(
            finding_type="HEALTH_POLICY_NOT_EVALUATED",
            severity=FindingSeverity.INFO,
            reason_code="HEALTH_POLICY_NOT_EVALUATED",
            title=f"Health policy not evaluated for {source_key}",
            description="Health policy remains declarative and has not been runtime-evaluated.",
            affected_dimension="policyHealth",
            decision_required=False,
            affected_source_system_keys=[source_key],
            evidence_references=evidence_references,
        )
    )


def evaluate_static_binding(
    binding: Mapping[str, Any],
    *,
    candidate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_key = str(binding["sourceSystemKey"])
    evidence_type = str(binding["evidenceType"])
    review_reasons = set(binding.get("reviewReasons", []))
    evidence_references = list(binding.get("evidenceReferences", []))

    configuration_review = evidence_type in {"alias_review", "namespace_review"}
    exact_evidence = evidence_type == "exact"

    if configuration_review:
        readiness = ReadinessState.REVIEW_REQUIRED.value
        configuration_state = HealthState.REVIEW_REQUIRED
        configuration_severity = FindingSeverity.MEDIUM
        evidence_classification = "REVIEW_REQUIRED"
    else:
        readiness = ReadinessState.RUNTIME_VERIFICATION_REQUIRED.value
        configuration_state = HealthState.UNKNOWN
        configuration_severity = FindingSeverity.LOW
        evidence_classification = "EVIDENCE_SUPPORTED"

    findings: list[dict[str, Any]] = []

    if "ALIAS_APPROVAL_REQUIRED" in review_reasons:
        findings.append(
            build_finding(
                finding_type="ALIAS_APPROVAL_PENDING",
                severity=FindingSeverity.MEDIUM,
                reason_code="ALIAS_APPROVAL_PENDING",
                title=f"Alias approval pending for {source_key}",
                description="Static source evidence requires an operator alias decision.",
                affected_dimension="configurationHealth",
                decision_required=True,
                affected_source_system_keys=[source_key],
                evidence_references=evidence_references,
            )
        )

    if "NAMESPACE_INTERPRETATION_REQUIRED" in review_reasons:
        findings.append(
            build_finding(
                finding_type="NAMESPACE_INTERPRETATION_PENDING",
                severity=FindingSeverity.MEDIUM,
                reason_code="NAMESPACE_INTERPRETATION_PENDING",
                title=f"Namespace interpretation pending for {source_key}",
                description="The source namespace requires an operator interpretation decision.",
                affected_dimension="configurationHealth",
                decision_required=True,
                affected_source_system_keys=[source_key],
                evidence_references=evidence_references,
            )
        )

    if "REGISTRY_APPROVAL_REQUIRED" in review_reasons:
        findings.append(
            build_finding(
                finding_type="REGISTRY_APPROVAL_PENDING",
                severity=FindingSeverity.LOW,
                reason_code="REGISTRY_APPROVAL_PENDING",
                title=f"Registry approval pending for {source_key}",
                description="Exact static evidence exists, but registry approval is still required.",
                affected_dimension="configurationHealth",
                decision_required=True,
                affected_source_system_keys=[source_key],
                evidence_references=evidence_references,
            )
        )

    findings.append(
        build_finding(
            finding_type="RUNTIME_EVIDENCE_UNAVAILABLE",
            severity=FindingSeverity.INFO,
            reason_code="RUNTIME_EVIDENCE_UNAVAILABLE",
            title=f"Runtime verification required for {source_key}",
            description="No runtime adapter evidence is connected; this is not an outage.",
            affected_dimension="runtimeObservationHealth",
            decision_required=False,
            affected_source_system_keys=[source_key],
            evidence_references=[],
        )
    )

    if candidate:
        _append_declaration_reference_findings(
            findings,
            source_key=source_key,
            candidate=candidate,
            evidence_references=evidence_references,
        )

    mapping_version = str((candidate or {}).get("mappingVersion", ""))
    schema_version = str((candidate or {}).get("schemaVersion", ""))

    record_identity = {
        "registryEntryId": binding["registryEntryId"],
        "sourceSystemKey": source_key,
        "projectionAuthority": "ONE-AIRPORT-A2-03",
    }

    record = {
        "integrationHealthId": sha256_digest(record_identity),
        "registryEntryId": str(binding["registryEntryId"]),
        "sourceSystemKey": source_key,
        "lifecycleState": str(binding["lifecycleState"]),
        "approvalState": str(binding["approvalState"]),
        "declarationHealth": build_health_dimension(
            state=HealthState.UNKNOWN,
            severity=FindingSeverity.INFO,
            reason_codes=["INTEGRATION_DECLARATION_PRESENT"],
            evidence_references=evidence_references,
            classification_state="DECLARED",
        ),
        "evidenceHealth": build_health_dimension(
            state=HealthState.UNKNOWN,
            severity=FindingSeverity.INFO,
            reason_codes=["STATIC_EVIDENCE_SUPPORTED" if exact_evidence else "STATIC_EVIDENCE_REVIEW_REQUIRED"],
            evidence_references=evidence_references,
            review_required=configuration_review,
            classification_state=evidence_classification,
        ),
        "configurationHealth": build_health_dimension(
            state=configuration_state,
            severity=configuration_severity,
            reason_codes=sorted(review_reasons),
            evidence_references=evidence_references,
            review_required=configuration_review,
            classification_state="REVIEW_REQUIRED" if configuration_review else "DECLARED",
        ),
        "runtimeObservationHealth": build_health_dimension(
            state=HealthState.UNKNOWN,
            severity=FindingSeverity.INFO,
            reason_codes=["RUNTIME_EVIDENCE_UNAVAILABLE"],
            runtime_observed=False,
            classification_state="UNKNOWN",
        ),
        "freshnessHealth": build_health_dimension(
            state=HealthState.NOT_APPLICABLE,
            severity=FindingSeverity.INFO,
            reason_codes=["NO_TIMESTAMPED_RUNTIME_SIGNAL"],
            runtime_observed=False,
            classification_state="NOT_APPLICABLE",
        ),
        "capabilityHealth": build_health_dimension(
            state=HealthState.UNKNOWN,
            severity=FindingSeverity.INFO,
            reason_codes=["CAPABILITIES_NOT_RUNTIME_VERIFIED"],
            evidence_references=evidence_references,
            classification_state="UNKNOWN",
        ),
        "policyHealth": build_health_dimension(
            state=HealthState.NOT_APPLICABLE,
            severity=FindingSeverity.INFO,
            reason_codes=["HEALTH_POLICY_NOT_EVALUATED"],
            classification_state="NOT_APPLICABLE",
        ),
        "readinessState": readiness,
        "findings": sorted(findings, key=lambda item: (item["findingType"], item["findingId"])),
        "evidenceReferences": evidence_references,
        "sourceRecordCount": int(binding["sourceRecordCount"]),
        "deviceEvidenceCount": int(binding["deviceEvidenceCount"]),
        "mappingVersionDeclaration": mapping_version or None,
        "schemaVersionDeclaration": schema_version or None,
        "generatedAtPolicy": "DETERMINISTIC_NO_VOLATILE_TIMESTAMP",
    }
    record["deterministicDigest"] = sha256_digest({k: v for k, v in record.items() if k != "deterministicDigest"})
    validate_health_record(record)
    return record
