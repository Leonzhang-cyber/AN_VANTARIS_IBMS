#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "AN_VANTARIS_ONE/registries/boundary-remediation-register.v1.json"
EXCEPTIONS = ROOT / "AN_VANTARIS_ONE/registries/boundary-exceptions.v1.json"
RULES = {f"A4-BND-{index:03d}" for index in range(1, 21)}
SOURCE_SEVERITIES = {"P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW", "REVIEW"}
TRIAGE_SEVERITIES = SOURCE_SEVERITIES
TRIAGE_STATUSES = {
    "CONFIRMED_VIOLATION", "CONFIRMED_LEGACY_DEBT", "REGISTERED_LEGACY_EXCEPTION",
    "REVIEW_REQUIRED", "LIKELY_FALSE_POSITIVE", "DUPLICATE_AGGREGATED", "NOT_APPLICABLE",
}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
PRIORITIES = {"P0", "P1", "P2", "P3", "DEFER"}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    return parser.parse_args()


def source_key(finding):
    material = {
        key: finding.get(key)
        for key in (
            "ruleId", "severity", "status", "path", "line", "symbol",
            "message", "evidence", "packageId", "owningModule",
            "exceptionId", "remediationGate",
        )
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":"))
    return "SRC-" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:20].upper()


def main():
    args = parse_args()
    errors = []
    try:
        register = json.loads(REGISTER.read_text(encoding="utf-8"))
        source = json.loads(Path(args.source).read_text(encoding="utf-8"))
        exceptions = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
    except Exception as exc:
        print("[ONE REMEDIATION REGISTER VALIDATION]")
        print(f"FAIL: {exc}")
        print("ONE_REMEDIATION_REGISTER_FAIL")
        return 1

    top = {
        "registryName", "registryVersion", "authority", "status", "sourceScanner",
        "sourceScannerVersion", "sourceMode", "generatedAtPolicy", "triagePolicy",
        "summary", "workstreams", "proposedTasks", "findings",
    }
    if not top.issubset(register):
        errors.append("missing required top-level fields")
    if register.get("registryName") != "VANTARIS ONE Boundary Remediation Register":
        errors.append("invalid registryName")
    if register.get("registryVersion") != "1.0.0" or register.get("authority") != "ONE-A5-P0-03":
        errors.append("invalid version or authority")
    if register.get("status") != "FROZEN_TRIAGE_BASELINE":
        errors.append("invalid status")
    if register.get("generatedAtPolicy") != "STATIC_ARCHITECTURE_BASELINE":
        errors.append("invalid generatedAtPolicy")

    findings = register.get("findings", [])
    workstreams = register.get("workstreams", [])
    tasks = register.get("proposedTasks", [])
    raw_findings = source.get("findings", [])
    exception_ids = {row["exceptionId"] for row in exceptions.get("exceptions", [])}
    if any(any(token in row.get("exactPath", "") + row.get("exactPattern", "") for token in ("*", "?", "[", "]")) for row in exceptions.get("exceptions", [])):
        errors.append("broad exception detected")

    remediation_ids = [row.get("remediationId") for row in findings]
    workstream_ids = [row.get("workstreamId") for row in workstreams]
    task_ids = [row.get("taskId") for row in tasks]
    if len(remediation_ids) != len(set(remediation_ids)):
        errors.append("duplicate remediationId")
    if len(workstream_ids) != len(set(workstream_ids)):
        errors.append("duplicate workstreamId")
    if len(task_ids) != len(set(task_ids)):
        errors.append("duplicate proposed taskId")

    required_finding_fields = {
        "remediationId", "sourceRuleId", "sourceSeverity", "triageSeverity", "triageStatus",
        "category", "workstreamId", "exactPath", "line", "symbol", "normalizedIssue",
        "evidenceSummary", "owningModule", "affectedPackage", "canonicalOwner", "targetState",
        "prerequisite", "remediationAction", "validationGate", "compatibilityRequirement",
        "rollbackRequirement", "exceptionId", "scannerConfidence", "implementationPriority",
        "proposedTaskId", "duplicateCount", "sourceFindingKeys",
    }
    represented = []
    for row in findings:
        if set(row) != required_finding_fields:
            errors.append(f"{row.get('remediationId')}: invalid finding structure")
        if row.get("sourceRuleId") not in RULES:
            errors.append(f"{row.get('remediationId')}: unknown source rule")
        if row.get("sourceSeverity") not in SOURCE_SEVERITIES or row.get("triageSeverity") not in TRIAGE_SEVERITIES:
            errors.append(f"{row.get('remediationId')}: invalid severity")
        if row.get("triageStatus") not in TRIAGE_STATUSES:
            errors.append(f"{row.get('remediationId')}: invalid triage status")
        if row.get("scannerConfidence") not in CONFIDENCE or row.get("implementationPriority") not in PRIORITIES:
            errors.append(f"{row.get('remediationId')}: invalid confidence or priority")
        if not isinstance(row.get("exactPath"), str) or not row["exactPath"]:
            errors.append(f"{row.get('remediationId')}: exactPath required")
        if row.get("workstreamId") not in set(workstream_ids):
            errors.append(f"{row.get('remediationId')}: unknown workstream")
        if row.get("proposedTaskId") not in set(task_ids):
            errors.append(f"{row.get('remediationId')}: unknown proposed task")
        else:
            task = next(item for item in tasks if item.get("taskId") == row.get("proposedTaskId"))
            if task.get("workstreamId") != row.get("workstreamId"):
                errors.append(f"{row.get('remediationId')}: proposed task workstream mismatch")
        if row.get("exceptionId") and row["exceptionId"] not in exception_ids:
            errors.append(f"{row.get('remediationId')}: unknown exceptionId")
        if row.get("triageStatus") == "REGISTERED_LEGACY_EXCEPTION" and not row.get("exceptionId"):
            errors.append(f"{row.get('remediationId')}: registered exception missing exceptionId")
        keys = row.get("sourceFindingKeys", [])
        if row.get("duplicateCount") != len(keys):
            errors.append(f"{row.get('remediationId')}: duplicateCount mismatch")
        represented.extend(keys)

    raw_keys = [source_key(row) for row in raw_findings]
    if len(raw_keys) != len(set(raw_keys)):
        errors.append("raw scanner finding keys are not unique")
    if Counter(represented) != Counter(raw_keys):
        missing = sorted(set(raw_keys) - set(represented))
        unknown = sorted(set(represented) - set(raw_keys))
        duplicates = sorted(key for key, count in Counter(represented).items() if count != 1)
        errors.append(f"finding coverage mismatch missing={len(missing)} unknown={len(unknown)} repeated={len(duplicates)}")

    raw_p0 = {source_key(row) for row in raw_findings if row.get("severity") == "P0_CRITICAL"}
    represented_p0 = {
        key
        for row in findings if row.get("sourceSeverity") == "P0_CRITICAL"
        for key in row.get("sourceFindingKeys", [])
    }
    if raw_p0 != represented_p0:
        errors.append("P0 source findings are not fully visible")

    finding_id_set = set(remediation_ids)
    for ws in workstreams:
        unknown = set(ws.get("findingIds", [])) - finding_id_set
        if unknown:
            errors.append(f"{ws.get('workstreamId')}: unknown finding IDs")
    for task in tasks:
        unknown = set(task.get("findingsCovered", [])) - finding_id_set
        if unknown:
            errors.append(f"{task.get('taskId')}: unknown finding IDs")

    summary = register.get("summary", {})
    if summary.get("rawFindingCount") != len(raw_findings):
        errors.append("raw finding summary mismatch")
    if summary.get("normalizedFindingCount") != len(findings):
        errors.append("normalized finding summary mismatch")
    if summary.get("deduplicatedRawFindingCount") != len(raw_findings) - len(findings):
        errors.append("deduplication summary mismatch")
    if summary.get("triageStatusCounts") != dict(sorted(Counter(row["triageStatus"] for row in findings).items())):
        errors.append("triage status summary mismatch")

    serialized = json.dumps(register, sort_keys=True)
    if re.search(r"\b20\d{2}-\d{2}-\d{2}\b", serialized):
        errors.append("timestamp/date found")
    if "/Users/" in serialized or "localhost" in serialized or "127.0.0.1" in serialized:
        errors.append("environment-specific value found")
    if "http://" in serialized or "https://" in serialized:
        errors.append("live endpoint found")

    checks = [
        ("JSON structure", not any("structure" in item or "top-level" in item or "registryName" in item for item in errors)),
        ("Finding coverage", not any("coverage" in item or "P0 source" in item for item in errors)),
        ("Deduplication", not any("duplicateCount" in item or "deduplication" in item or "repeated" in item for item in errors)),
        ("Exception references", not any("exception" in item.lower() for item in errors)),
        ("Workstreams", not any("workstream" in item.lower() for item in errors)),
        ("Proposed tasks", not any("task" in item.lower() for item in errors)),
        ("Count reconciliation", not any("summary mismatch" in item for item in errors)),
        ("UFMS boundary", not any("endpoint" in item or "environment-specific" in item for item in errors)),
    ]
    print("[ONE REMEDIATION REGISTER VALIDATION]")
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_REMEDIATION_REGISTER_FAIL")
        return 1
    print("ONE_REMEDIATION_REGISTER_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
