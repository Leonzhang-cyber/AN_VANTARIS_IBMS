#!/usr/bin/env python3
"""Validate the VANTARIS ONE legacy ownership migration register."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWNER_MAP = ROOT / "AN_VANTARIS_ONE/registries/legacy-table-owner-map.v1.json"
MIGRATION = ROOT / "AN_VANTARIS_ONE/registries/legacy-ownership-migration-register.v1.json"
BUILDER = ROOT / "scripts/validation/build-one-legacy-ownership-inventory.py"
CANONICAL = ROOT / "contracts/registry/canonical-objects.v1.json"
CONTRACTS = ROOT / "contracts/registry/contract-namespaces.v1.json"
PACKAGES = ROOT / "AN_VANTARIS_ONE/registries/package-registry.v1.json"
APIS = ROOT / "AN_VANTARIS_ONE/registries/api-namespace-registry.v1.json"
EXCEPTIONS = ROOT / "AN_VANTARIS_ONE/registries/boundary-exceptions.v1.json"
ROUTES = ROOT / "AN_VANTARIS_ONE/registries/backend-route-inventory.v1.json"

STORE_TYPES = {
    "SQL_TABLE", "ORM_MODEL", "JSON_FILE", "JSONL_LEDGER",
    "LOCAL_FILESYSTEM", "IN_MEMORY_STORE", "EXTERNAL_STORE_REFERENCE", "UNKNOWN",
}
OWNERSHIP = {
    "CORRECT_OWNER", "LEGACY_OWNER", "MIXED_RESPONSIBILITY", "PROJECTION_ONLY",
    "LOCAL_FALLBACK", "PLACEHOLDER", "REVIEW_REQUIRED",
}
MIGRATION_CLASSES = {
    "NO_MIGRATION", "CONTRACT_FIRST", "READ_FACADE", "STRANGLER_MIGRATION",
    "DATA_COPY_AND_RECONCILE", "OWNERSHIP_SPLIT", "RETIRE_AFTER_PARITY",
    "REVIEW_REQUIRED",
}
IMPLEMENTATION = {
    "CONTRACT_REQUIRED", "TARGET_PROVIDER_REQUIRED", "READ_MIGRATION_READY",
    "WRITE_MIGRATION_BLOCKED", "RECONCILIATION_REQUIRED",
    "LEGACY_EXCEPTION_ACTIVE", "REVIEW_REQUIRED", "NO_ACTION_REQUIRED",
}
REVIEW_TYPES = {
    "PHYSICAL_STORE_AMBIGUITY", "SEMANTIC_OWNER_AMBIGUITY",
    "TABLE_RELATIONSHIP_UNKNOWN", "IDENTIFIER_MAPPING_UNKNOWN",
    "RETENTION_REQUIREMENT_UNKNOWN", "DUAL_WRITE_REVIEW", "EXTERNAL_DEPENDENCY",
    "UFMS_LIVE_VERIFICATION", "CREDENTIAL_SEPARATION",
    "LEGACY_ROUTE_DEPENDENCY", "PROVIDER_BEHAVIOR_UNKNOWN",
}
WAVE_ORDER = [
    "WAVE-0-CONTRACTS", "WAVE-1-TARGET-PROVIDERS", "WAVE-2-READ-MIGRATION",
    "WAVE-3-WRITE-CUTOVER", "WAVE-4-RECONCILIATION",
    "WAVE-5-LEGACY-RETIREMENT",
]
REQUIRED_EXCEPTIONS = {
    "LEGACY-IOT-DEVICE-MODEL-001",
    "LEGACY-REPORTS-AUDIT-001",
    "LEGACY-UMMS-WORKORDER-001",
    "LEGACY-UCDE-EVIDENCE-001",
}


def load(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name}: {exc}")
        return {}


def owner_summary(stores: list[dict], unresolved: list[dict]) -> dict:
    modules = Counter(row.get("currentModule") for row in stores)
    owners = Counter(row.get("canonicalOwner") for row in stores)
    migrations = Counter(row.get("migrationClass") for row in stores)
    return {
        "totalStores": len(stores),
        "sqlTables": sum(row.get("storeType") == "SQL_TABLE" for row in stores),
        "ormModels": sum(row.get("storeType") == "ORM_MODEL" for row in stores),
        "jsonStores": sum(row.get("storeType") == "JSON_FILE" for row in stores),
        "jsonlStores": sum(row.get("storeType") == "JSONL_LEDGER" for row in stores),
        "localFilesystemStores": sum(row.get("storeType") == "LOCAL_FILESYSTEM" for row in stores),
        "inMemoryStores": sum(row.get("storeType") == "IN_MEMORY_STORE" for row in stores),
        "correctOwnerStores": sum(row.get("ownershipStatus") == "CORRECT_OWNER" for row in stores),
        "legacyOwnerStores": sum(row.get("ownershipStatus") == "LEGACY_OWNER" for row in stores),
        "mixedResponsibilityStores": sum(row.get("ownershipStatus") == "MIXED_RESPONSIBILITY" for row in stores),
        "placeholderStores": sum(row.get("ownershipStatus") == "PLACEHOLDER" for row in stores),
        "unresolvedStores": len(unresolved),
        "storesByCurrentModule": dict(sorted(modules.items())),
        "storesByCanonicalOwner": dict(sorted(owners.items())),
        "storesByMigrationClass": dict(sorted(migrations.items())),
    }


def migration_summary(conflicts: list[dict], tasks: list[dict], reviews: list[dict]) -> dict:
    statuses = Counter(row.get("implementationStatus") for row in conflicts)
    waves = Counter(row.get("migrationWave") for row in conflicts)
    owners = Counter(row.get("canonicalOwner") for row in conflicts)
    packages = Counter(row.get("targetPackage") for row in conflicts)
    return {
        "totalConflicts": len(conflicts),
        "P0ExceptionConflicts": sum(bool(row.get("exceptionIds")) for row in conflicts),
        "contractRequired": statuses["CONTRACT_REQUIRED"],
        "targetProviderRequired": statuses["TARGET_PROVIDER_REQUIRED"],
        "writeMigrationBlocked": statuses["WRITE_MIGRATION_BLOCKED"],
        "reconciliationRequired": statuses["RECONCILIATION_REQUIRED"],
        "activeLegacyExceptions": sum(len(row.get("exceptionIds", [])) for row in conflicts),
        "proposedTaskCount": len(tasks),
        "reviewQueueCount": len(reviews),
        "conflictsByMigrationWave": dict(sorted(waves.items())),
        "conflictsByCanonicalOwner": dict(sorted(owners.items())),
        "conflictsByTargetPackage": dict(sorted(packages.items())),
    }


def deterministic(path: Path, value: dict) -> bool:
    return path.read_text(encoding="utf-8") == json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    errors: list[str] = []
    for path in (OWNER_MAP, MIGRATION):
        if not path.is_file():
            errors.append(f"missing registry: {path.name}")
    owner_map = load(OWNER_MAP, errors) if OWNER_MAP.is_file() else {}
    migration = load(MIGRATION, errors) if MIGRATION.is_file() else {}
    canonical_doc = load(CANONICAL, errors)
    contract_doc = load(CONTRACTS, errors)
    package_doc = load(PACKAGES, errors)
    api_doc = load(APIS, errors)
    exception_doc = load(EXCEPTIONS, errors)
    route_doc = load(ROUTES, errors)

    owner_top = {
        "registryName", "registryVersion", "authority", "status",
        "generatedAtPolicy", "extractionPolicy", "summary",
        "physicalStores", "unresolvedStores",
    }
    migration_required_top = {
        "registryName", "registryVersion", "authority", "status",
        "generatedAtPolicy", "migrationPrinciples", "ownershipConflicts",
        "migrationWaves", "compatibilityPolicies", "reconciliationPolicies",
        "rollbackPolicies", "exceptionRetirementPlan", "reviewQueue", "summary",
        "proposedTasks", "dualWritePolicy",
    }
    if set(owner_map) != owner_top:
        errors.append("owner map invalid top-level fields")
    if set(migration) != migration_required_top:
        errors.append("migration register invalid top-level fields")
    fixed = [
        (owner_map, "registryName", "VANTARIS ONE Legacy Physical Store Owner Map"),
        (owner_map, "status", "FROZEN_LEGACY_STORE_BASELINE"),
        (migration, "registryName", "VANTARIS ONE Legacy Ownership Migration Register"),
        (migration, "status", "FROZEN_FOR_MIGRATION_IMPLEMENTATION"),
    ]
    for doc, field, expected in fixed:
        if doc.get(field) != expected:
            errors.append(f"invalid {field}")
    for doc in (owner_map, migration):
        if doc.get("registryVersion") != "1.0.0" or doc.get("authority") != "ONE-A5-P0-08":
            errors.append("invalid version or authority")
        if doc.get("generatedAtPolicy") != "STATIC_ARCHITECTURE_BASELINE":
            errors.append("invalid generatedAtPolicy")

    canonical_names = {row.get("objectName") for row in canonical_doc.get("objects", [])}
    contract_names = {row.get("namespace") for row in contract_doc.get("namespaces", [])}
    package_ids = {row.get("packageId") for row in package_doc.get("packages", [])}
    api_names = {row.get("namespace") for row in api_doc.get("apiNamespaces", [])}
    exception_ids = {row.get("exceptionId") for row in exception_doc.get("exceptions", [])}
    route_ids = {row.get("routeId") for row in route_doc.get("routes", [])}

    stores = owner_map.get("physicalStores", [])
    unresolved = owner_map.get("unresolvedStores", [])
    store_ids = [row.get("storeId") for row in stores]
    physical_names = [row.get("physicalName") for row in stores]
    if len(store_ids) != len(set(store_ids)):
        errors.append("duplicate physical store ID")
    if len(physical_names) != len(set(physical_names)):
        errors.append("physical store represented more than once")
    if store_ids != sorted(store_ids):
        errors.append("physical stores are not deterministically sorted")
    store_fields = {
        "storeId", "storeType", "sourcePath", "line", "symbol", "physicalName",
        "currentModule", "currentPackage", "currentSemanticObjects",
        "currentPersistenceRole", "canonicalObjects", "canonicalOwner",
        "targetSystemOfRecord", "targetPackage", "ownershipStatus",
        "migrationClass", "compatibilityFacadeRequired", "dualReadAllowed",
        "dualWriteAllowed", "dataReconciliationRequired", "auditRequired",
        "evidenceRequired", "retentionRequirement", "migrationPrerequisites",
        "proposedMigrationTask", "rollbackRequirement", "removalGate",
        "scannerConfidence", "notes",
    }
    for row in stores:
        sid = row.get("storeId")
        if set(row) != store_fields:
            errors.append(f"{sid}: invalid store structure")
        path = row.get("sourcePath", "")
        if not path or path.startswith("/") or "/Users/" in path:
            errors.append(f"{sid}: source path is not repository-relative")
        if not row.get("currentModule") or not row.get("canonicalOwner") or not row.get("targetSystemOfRecord"):
            errors.append(f"{sid}: current or canonical owner missing")
        if row.get("storeType") not in STORE_TYPES:
            errors.append(f"{sid}: invalid store type")
        if row.get("ownershipStatus") not in OWNERSHIP:
            errors.append(f"{sid}: invalid ownership status")
        if row.get("migrationClass") not in MIGRATION_CLASSES:
            errors.append(f"{sid}: invalid migration class")
        unknown_objects = set(row.get("canonicalObjects", [])) - canonical_names
        if unknown_objects:
            errors.append(f"{sid}: unknown canonical object {sorted(unknown_objects)}")
        if row.get("targetPackage") not in package_ids:
            errors.append(f"{sid}: unknown target package")
        if row.get("dualWriteAllowed") is not False:
            errors.append(f"{sid}: dual write must default false")
        if not row.get("rollbackRequirement") or not row.get("removalGate"):
            errors.append(f"{sid}: rollback or removal gate missing")
    unresolved_ids = [row.get("storeId") for row in unresolved]
    if len(unresolved_ids) != len(set(unresolved_ids)):
        errors.append("duplicate unresolved store ID")
    if owner_map.get("summary") != owner_summary(stores, unresolved):
        errors.append("physical-store summary mismatch")

    store_id_set = set(store_ids)
    conflicts = migration.get("ownershipConflicts", [])
    conflict_ids = [row.get("conflictId") for row in conflicts]
    if len(conflict_ids) != len(set(conflict_ids)):
        errors.append("duplicate ownership conflict ID")
    if conflict_ids != sorted(conflict_ids):
        errors.append("ownership conflicts are not deterministically sorted")
    conflict_fields = {
        "conflictId", "title", "sourceEvidence", "currentOwner",
        "currentPhysicalStores", "affectedObjects", "canonicalOwner",
        "targetSystemOfRecord", "targetPackage", "sourcePackages",
        "targetContracts", "currentRoutes", "targetApiNamespace",
        "targetEventContracts", "migrationClass", "migrationWave",
        "compatibilityFacade", "readMigration", "writeMigration",
        "identifierMapping", "dataReconciliation", "auditMigration",
        "evidenceMigration", "retentionMigration", "packageImpact",
        "deploymentImpact", "prerequisites", "explicitNonScope",
        "validationGates", "rollbackPlan", "exceptionIds",
        "exceptionRetirementGate", "proposedTasks", "implementationStatus",
        "scannerConfidence", "reviewReason", "notes",
    }
    for row in conflicts:
        cid = row.get("conflictId")
        if set(row) != conflict_fields:
            errors.append(f"{cid}: invalid conflict structure")
        if not row.get("currentOwner") or not row.get("canonicalOwner") or not row.get("targetSystemOfRecord"):
            errors.append(f"{cid}: ownership fields missing")
        if not set(row.get("currentPhysicalStores", [])) <= store_id_set:
            errors.append(f"{cid}: unknown physical store reference")
        if row.get("targetPackage") not in package_ids:
            errors.append(f"{cid}: unknown target package")
        if set(row.get("sourcePackages", [])) - package_ids:
            errors.append(f"{cid}: unknown source package")
        if set(row.get("targetContracts", [])) - contract_names:
            errors.append(f"{cid}: unknown target contract")
        if row.get("targetApiNamespace") not in api_names:
            errors.append(f"{cid}: unknown target API namespace")
        if set(row.get("currentRoutes", [])) - route_ids:
            errors.append(f"{cid}: unknown current route")
        if row.get("migrationClass") not in MIGRATION_CLASSES:
            errors.append(f"{cid}: invalid migration class")
        if row.get("migrationWave") not in WAVE_ORDER:
            errors.append(f"{cid}: invalid migration wave")
        if row.get("implementationStatus") not in IMPLEMENTATION:
            errors.append(f"{cid}: invalid implementation status")
        if set(row.get("exceptionIds", [])) - exception_ids:
            errors.append(f"{cid}: unknown exception ID")
        if not row.get("rollbackPlan") or not row.get("validationGates"):
            errors.append(f"{cid}: rollback or validation gates missing")
        if any("one-adapter" in str(item).lower() and "no generic" not in str(item).lower() for item in row.get("explicitNonScope", [])):
            errors.append(f"{cid}: generic one-adapter proposed")

    conflicts_by_id = {row.get("conflictId"): row for row in conflicts}
    required_conflict_map = {
        "OWN-LEGACY-DEVICE-001": "LEGACY-IOT-DEVICE-MODEL-001",
        "OWN-REPORTS-AUDIT-001": "LEGACY-REPORTS-AUDIT-001",
        "OWN-UMMS-WORKORDER-001": "LEGACY-UMMS-WORKORDER-001",
        "OWN-UCDE-EVIDENCE-001": "LEGACY-UCDE-EVIDENCE-001",
    }
    for cid, exception in required_conflict_map.items():
        if cid not in conflicts_by_id or exception not in conflicts_by_id[cid].get("exceptionIds", []):
            errors.append(f"{cid}: required exception mapping missing")
    represented_exceptions = {
        exception for row in conflicts for exception in row.get("exceptionIds", [])
    }
    if represented_exceptions != REQUIRED_EXCEPTIONS:
        errors.append("four exact legacy exceptions are not represented exactly")
    if REQUIRED_EXCEPTIONS != exception_ids:
        errors.append("upstream exception registry differs from four expected exact exceptions")

    umms = conflicts_by_id.get("OWN-UMMS-WORKORDER-001", {})
    if "ONE Work Management" not in umms.get("canonicalOwner", "") or umms.get("targetPackage") != "PKG-WORK-MANAGEMENT":
        errors.append("UMMS retains generic WorkOrder ownership")
    ucde = conflicts_by_id.get("OWN-UCDE-EVIDENCE-001", {})
    if "Evidence Center" not in ucde.get("canonicalOwner", "") or ucde.get("targetPackage") != "PKG-EVIDENCE-CENTER":
        errors.append("UCDE retains EvidenceRecord ownership")
    edge = conflicts_by_id.get("OWN-EDGE-CANONICAL-DEVICE-001", {})
    if "ONE Asset Graph" not in edge.get("canonicalOwner", "") or "does not retain canonical Device" not in " ".join(edge.get("notes", [])):
        errors.append("EDGE retains canonical Device/Point ownership")
    reports = conflicts_by_id.get("OWN-REPORTS-AUDIT-001", {})
    if reports.get("canonicalOwner") != "Governance & Security" or reports.get("targetPackage") != "PKG-GOVERNANCE-SECURITY":
        errors.append("Reports remains AuditRecord system of record")
    ucore = conflicts_by_id.get("OWN-UCORE-ASSET-001", {})
    if "Asset Graph" not in ucore.get("canonicalOwner", "") or "must not become" not in " ".join(ucore.get("notes", [])):
        errors.append("UCore becomes Asset Graph system of record")
    ufms = conflicts_by_id.get("OWN-UFMS-PLACEHOLDER-001", {})
    if ufms.get("canonicalOwner") != "UFMS" or ufms.get("targetSystemOfRecord") != "UFMS external product":
        errors.append("UFMS external integration boundary invalid")

    waves = migration.get("migrationWaves", [])
    if [row.get("waveId") for row in waves] != WAVE_ORDER:
        errors.append("migration waves are missing or out of order")
    wave_fields = {
        "waveId", "objective", "prerequisites", "allowedChanges",
        "prohibitedChanges", "validationGates", "rollbackRequirements", "exitCriteria",
    }
    if any(set(row) != wave_fields for row in waves):
        errors.append("migration wave structure invalid")

    facades = migration.get("compatibilityPolicies", [])
    facade_ids = {row.get("facadeType") for row in facades}
    required_facades = {
        "READ_ONLY_FACADE", "LEGACY_ROUTE_PROXY", "LEGACY_DTO_TRANSLATOR",
        "IDENTIFIER_MAPPING", "PROJECTION_ADAPTER", "EXPORT_COMPATIBILITY",
        "NO_FACADE_ALLOWED",
    }
    if facade_ids != required_facades or len(facades) != len(required_facades):
        errors.append("compatibility façade types incomplete")
    if any(row.get("businessWriteAllowed") is not False for row in facades):
        errors.append("compatibility façade permits business writes")

    dual = migration.get("dualWritePolicy", {})
    if dual.get("defaultAllowed") is not False or dual.get("approvedProposals") != []:
        errors.append("dual write is enabled or approved")
    mandatory_controls = {
        "authoritativeWriteResult", "durableOutboxOrTransactionBoundary",
        "deterministicIdempotency", "reconciliationLedger", "failureRecovery",
        "audit", "cutoverPlan", "rollbackPlan", "boundedDuration", "ownerApproval",
    }
    if set(dual.get("mandatoryControlsForAnyFutureProposal", [])) != mandatory_controls:
        errors.append("dual-write mandatory controls incomplete")

    reconciliation = migration.get("reconciliationPolicies", [])
    required_dimensions = {
        "RECORD_COUNT", "GLOBAL_ID", "SOURCE_ID", "RELATIONSHIP_COUNT", "STATE",
        "STATUS", "TIMESTAMP", "DIGEST", "AUDIT_LINK", "EVIDENCE_PROVENANCE",
        "TENANT_SCOPE", "SITE_SCOPE", "ORPHAN_REFERENCE", "DUPLICATE_ID",
    }
    if {row.get("dimension") for row in reconciliation} != required_dimensions:
        errors.append("reconciliation dimensions incomplete")
    if any(row.get("repairAllowed") is not False or row.get("auditRequired") is not True for row in reconciliation):
        errors.append("reconciliation repair or audit policy invalid")

    rollback = migration.get("rollbackPolicies", [])
    if not rollback or any(not row.get("requirements") or not row.get("trigger") for row in rollback):
        errors.append("rollback policies incomplete")

    retirement = migration.get("exceptionRetirementPlan", [])
    retirement_ids = [row.get("exceptionId") for row in retirement]
    if set(retirement_ids) != REQUIRED_EXCEPTIONS or len(retirement_ids) != len(set(retirement_ids)):
        errors.append("exception retirement plan incomplete")
    for row in retirement:
        if row.get("exceptionId") not in exception_ids or row.get("conflictId") not in conflicts_by_id:
            errors.append(f"{row.get('exceptionId')}: invalid retirement mapping")
        for field in ("targetParityGate", "reconciliationGate", "rollbackGate", "strictScannerGate", "retirementApproval", "finalRemovalTask"):
            if not row.get(field):
                errors.append(f"{row.get('exceptionId')}: retirement gate missing {field}")

    tasks = migration.get("proposedTasks", [])
    required_tasks = {f"ONE-A5-P1-{number:02d}" for number in range(7, 18)}
    task_ids = {row.get("taskId") for row in tasks}
    if task_ids != required_tasks or len(tasks) != len(required_tasks):
        errors.append("proposed migration tasks incomplete")
    for row in tasks:
        if not set(row.get("conflictIds", [])) <= set(conflict_ids):
            errors.append(f"{row.get('taskId')}: unknown conflict")
        if "push" in json.dumps(row).lower():
            errors.append(f"{row.get('taskId')}: push instruction found")

    reviews = migration.get("reviewQueue", [])
    review_ids = [row.get("reviewId") for row in reviews]
    if len(review_ids) != len(set(review_ids)):
        errors.append("duplicate review ID")
    for row in reviews:
        if row.get("conflictId") not in conflicts_by_id:
            errors.append(f"{row.get('reviewId')}: unknown conflict")
        if row.get("storeId") and row.get("storeId") not in store_id_set:
            errors.append(f"{row.get('reviewId')}: unknown store")
        if row.get("reviewType") not in REVIEW_TYPES:
            errors.append(f"{row.get('reviewId')}: invalid review type")

    if migration.get("summary") != migration_summary(conflicts, tasks, reviews):
        errors.append("migration summary mismatch")

    serialized = json.dumps({"ownerMap": owner_map, "migration": migration}, sort_keys=True)
    if re.search(r"\b20\d{2}-\d{2}-\d{2}\b", serialized) or "/Users/" in serialized:
        errors.append("timestamp or absolute user path found")
    if re.search(r"https?://|localhost|127\.0\.0\.1", serialized, re.IGNORECASE):
        errors.append("live endpoint found")
    if re.search(r"UFMS.{0,40}(https?://|localhost|endpoint\s*=)", serialized, re.IGNORECASE):
        errors.append("live UFMS endpoint found")
    if OWNER_MAP.is_file() and owner_map and not deterministic(OWNER_MAP, owner_map):
        errors.append("owner map JSON formatting is not deterministic")
    if MIGRATION.is_file() and migration and not deterministic(MIGRATION, migration):
        errors.append("migration register JSON formatting is not deterministic")

    completed = subprocess.run(
        [sys.executable, str(BUILDER), "--root", str(ROOT), "--format", "json"],
        capture_output=True, text=True, check=False,
    )
    extraction_deterministic = (
        completed.returncode == 0
        and OWNER_MAP.is_file()
        and OWNER_MAP.read_text(encoding="utf-8") == completed.stdout
    )
    if not extraction_deterministic:
        errors.append("committed owner map differs from deterministic builder output")

    checks = [
        ("Physical store inventory", not any("store" in item.lower() and "unknown" not in item.lower() for item in errors)),
        ("Canonical ownership", not any(term in item for item in errors for term in ("owner missing", "retains", "becomes Asset Graph", "ownership fields"))),
        ("Package references", not any("package" in item.lower() for item in errors)),
        ("Contract references", not any("contract" in item.lower() for item in errors)),
        ("Exception coverage", not any("exception" in item.lower() for item in errors)),
        ("Migration waves", not any("wave" in item.lower() for item in errors)),
        ("Dual-write policy", not any("dual write" in item.lower() or "dual-write" in item.lower() for item in errors)),
        ("Reconciliation policy", not any("reconciliation" in item.lower() for item in errors)),
        ("Rollback policy", not any("rollback" in item.lower() for item in errors)),
        ("UFMS boundary", not any("UFMS" in item for item in errors)),
        ("Deterministic extraction", extraction_deterministic),
    ]
    print("[ONE LEGACY OWNERSHIP REGISTER VALIDATION]")
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_LEGACY_OWNERSHIP_REGISTER_FAIL")
        return 1
    print("ONE_LEGACY_OWNERSHIP_REGISTER_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
