"""Alias and label approval packages for airport reconciliation."""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from ...reconciliation.models import sha256_digest
from .constants import SOURCE_NAMESPACE_PROPOSALS, SYSTEM_ALIAS_PROPOSALS
from .decisions import classify_label


def build_alias_approval_package(
    *,
    devices: Sequence[Mapping[str, Any]],
    classification_by_row: Mapping[tuple[str, int], Mapping[str, Any]],
) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []

    alias_counts: Counter[str] = Counter()
    for device in devices:
        key = (str(device.get("sourceWorksheet", "")), int(device.get("sourceRowNumber", 0)))
        binding = classification_by_row.get(key, {})
        embedded = str(binding.get("embeddedSystemCode", "")).upper()
        if embedded in {"CCT", "PAS"} and str(binding.get("systemMappingStatus", "")) == "ALIAS_CANDIDATE":
            alias_counts[embedded] += 1

    for source_value, target_value, category in SYSTEM_ALIAS_PROPOSALS:
        count = alias_counts.get(source_value, 0)
        if not count:
            continue
        proposal = {
            "proposalId": sha256_digest({"proposalType": "SYSTEM_ALIAS", "sourceValue": source_value}),
            "proposalType": "SYSTEM_ALIAS",
            "sourceValueDigest": sha256_digest({"embeddedSystemCode": source_value}),
            "targetValue": target_value,
            "genericCategory": category,
            "affectedRecordCount": count,
            "evidenceBasis": "A1-03 classification alias candidate",
            "riskClass": "MEDIUM",
            "recommendedDecision": "APPROVAL_REQUIRED",
            "currentAuthority": "EVIDENCE_ONLY",
            "requiredAuthority": "CUSTOMER_MAPPING_APPROVED",
            "decisionStatus": "APPROVAL_REQUIRED",
        }
        proposals.append(proposal)

    namespace_count = sum(
        1
        for device in devices
        if str(classification_by_row.get(
            (str(device.get("sourceWorksheet", "")), int(device.get("sourceRowNumber", 0))), {}
        ).get("sourceNamespaceCode", "")) == "SCN"
    )
    for namespace, review_type in SOURCE_NAMESPACE_PROPOSALS:
        if not namespace_count:
            continue
        proposals.append(
            {
                "proposalId": sha256_digest({"proposalType": "SOURCE_NAMESPACE", "namespace": namespace}),
                "proposalType": "SOURCE_NAMESPACE",
                "sourceValueDigest": sha256_digest({"sourceNamespaceCode": namespace}),
                "targetValue": review_type,
                "genericCategory": "TELECOMMUNICATION",
                "affectedRecordCount": namespace_count,
                "evidenceBasis": "A1-03 SCN semantic review required",
                "riskClass": "HIGH",
                "recommendedDecision": "APPROVAL_REQUIRED",
                "currentAuthority": "UNRESOLVED",
                "requiredAuthority": "CUSTOMER_MAPPING_APPROVED",
                "decisionStatus": "APPROVAL_REQUIRED",
            }
        )

    label_rules: dict[str, dict[str, Any]] = {}
    for device in devices:
        key = (str(device.get("sourceWorksheet", "")), int(device.get("sourceRowNumber", 0)))
        binding = classification_by_row.get(key, {})
        source_label = str(device.get("sourceDeviceType", ""))
        type_code = str(binding.get("embeddedDeviceTypeCode", ""))
        label_status, normalized = classify_label(source_label, type_code)
        if label_status == "LABEL_EXACT":
            continue
        rule_key = f"{type_code}:{label_status}:{normalized or ''}"
        label_rules.setdefault(
            rule_key,
            {
                "proposalType": "DEVICE_LABEL_NORMALIZATION",
                "sourceValueDigest": sha256_digest({"sourceDeviceTypeLabel": source_label, "deviceTypeCode": type_code}),
                "targetValue": normalized or source_label,
                "labelClassification": label_status,
                "deviceTypeCode": type_code,
                "affectedRecordCount": 0,
                "evidenceBasis": "A1-03 device type column conflict with semantic equivalence candidate",
                "riskClass": "LOW",
                "recommendedDecision": "APPROVAL_REQUIRED",
                "currentAuthority": "EVIDENCE_ONLY",
                "requiredAuthority": "CUSTOMER_MAPPING_APPROVED",
                "decisionStatus": "APPROVAL_REQUIRED",
            },
        )
        label_rules[rule_key]["affectedRecordCount"] += 1

    for rule in label_rules.values():
        proposals.append(
            {
                "proposalId": sha256_digest(
                    {
                        "proposalType": rule["proposalType"],
                        "sourceValueDigest": rule["sourceValueDigest"],
                        "targetValue": rule["targetValue"],
                    }
                ),
                **rule,
            }
        )

    proposals.sort(key=lambda item: item["proposalId"])
    return proposals
