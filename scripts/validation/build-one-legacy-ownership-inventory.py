#!/usr/bin/env python3
"""Build the deterministic VANTARIS ONE legacy physical-store ownership map."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def stable_id(kind: str, value: str) -> str:
    return f"STORE-{kind}-{hashlib.sha256(value.encode()).hexdigest()[:12].upper()}"


TABLE_MAP = {
    "imbs_device": {
        "module": "Legacy IoT", "package": "PKG-ASSET-GRAPH",
        "objects": ["Device", "Point", "Tag", "ConnectorRuntime"],
        "canonical": ["Device", "Point", "Tag", "ConnectorRuntime"],
        "owner": "ONE Asset Graph / AN_VANTARIS_EDGE / Governance & Security",
        "sor": "ONE Asset Graph and AN_VANTARIS_EDGE with credential references",
        "targetPackage": "PKG-ASSET-GRAPH", "status": "MIXED_RESPONSIBILITY",
        "migration": "OWNERSHIP_SPLIT", "task": "ONE-A5-P1-07",
    },
    "imbs_standard_field": {
        "module": "Legacy IoT", "package": "PKG-UNIFIED-DATA-MODEL",
        "objects": ["Point", "Tag"], "canonical": ["Point", "Tag"],
        "owner": "Unified Data Model / ONE Asset Graph", "sor": "Unified Data Model and ONE Asset Graph",
        "targetPackage": "PKG-UNIFIED-DATA-MODEL", "status": "MIXED_RESPONSIBILITY",
        "migration": "CONTRACT_FIRST", "task": "ONE-A5-P1-07",
    },
    "imbs_field_mapping": {
        "module": "Legacy IoT", "package": "PKG-UNIFIED-DATA-MODEL",
        "objects": ["MappingCandidate", "Point"], "canonical": ["MappingCandidate", "Point"],
        "owner": "AN_VANTARIS_EDGE / ONE Asset Graph", "sor": "AN_VANTARIS_EDGE mapping execution and ONE Asset Graph Point",
        "targetPackage": "PKG-EDGE", "status": "MIXED_RESPONSIBILITY",
        "migration": "OWNERSHIP_SPLIT", "task": "ONE-A5-P1-09",
    },
    "imbs_method_mapping": {
        "module": "Legacy IoT", "package": "PKG-UNIFIED-DATA-MODEL",
        "objects": ["MappingCandidate", "ConnectorRuntime"], "canonical": ["MappingCandidate", "ConnectorRuntime"],
        "owner": "AN_VANTARIS_EDGE", "sor": "AN_VANTARIS_EDGE",
        "targetPackage": "PKG-EDGE", "status": "LEGACY_OWNER",
        "migration": "STRANGLER_MIGRATION", "task": "ONE-A5-P1-09",
    },
    "imbs_standard_method": {
        "module": "Legacy IoT", "package": "PKG-UNIFIED-DATA-MODEL",
        "objects": ["MappingCandidate"], "canonical": ["MappingCandidate"],
        "owner": "Unified Data Model / AN_VANTARIS_EDGE", "sor": "Unified Data Model contracts and AN_VANTARIS_EDGE execution",
        "targetPackage": "PKG-UNIFIED-DATA-MODEL", "status": "MIXED_RESPONSIBILITY",
        "migration": "CONTRACT_FIRST", "task": "ONE-A5-P1-07",
    },
    "imbs_relationship": {
        "module": "Legacy DID", "package": "PKG-GOVERNANCE-SECURITY",
        "objects": ["Identity relationship"], "canonical": [],
        "owner": "Governance & Security", "sor": "Governance & Security",
        "targetPackage": "PKG-GOVERNANCE-SECURITY", "status": "LEGACY_OWNER",
        "migration": "CONTRACT_FIRST", "task": "ONE-A5-P1-16",
    },
    "imbs_users": {
        "module": "Legacy DID", "package": "PKG-GOVERNANCE-SECURITY",
        "objects": ["Identity", "Credential reference"], "canonical": [],
        "owner": "Governance & Security", "sor": "Governance & Security identity service",
        "targetPackage": "PKG-GOVERNANCE-SECURITY", "status": "LEGACY_OWNER",
        "migration": "STRANGLER_MIGRATION", "task": "ONE-A5-P1-16",
    },
    "imbs_vc_anchor": {
        "module": "Legacy DID", "package": "PKG-GOVERNANCE-SECURITY",
        "objects": ["HashAnchor"], "canonical": ["HashAnchor"],
        "owner": "Evidence Center / Trust", "sor": "Governance & Security / Trust",
        "targetPackage": "PKG-GOVERNANCE-SECURITY", "status": "MIXED_RESPONSIBILITY",
        "migration": "READ_FACADE", "task": "ONE-A5-P1-16",
    },
    "imbs_vc_revocation": {
        "module": "Legacy DID", "package": "PKG-GOVERNANCE-SECURITY",
        "objects": ["HashAnchor"], "canonical": ["HashAnchor"],
        "owner": "Evidence Center / Trust", "sor": "Governance & Security / Trust",
        "targetPackage": "PKG-GOVERNANCE-SECURITY", "status": "MIXED_RESPONSIBILITY",
        "migration": "READ_FACADE", "task": "ONE-A5-P1-16",
    },
    "imbs_entity_type": {
        "module": "Legacy DID / UCore", "package": "PKG-UCORE",
        "objects": ["Classification metadata"], "canonical": [],
        "owner": "Unified Data Model", "sor": "Unified Data Model contracts",
        "targetPackage": "PKG-UNIFIED-DATA-MODEL", "status": "MIXED_RESPONSIBILITY",
        "migration": "CONTRACT_FIRST", "task": "ONE-A5-P1-16",
    },
    "imbs_permission": {
        "module": "Legacy DID / UCore", "package": "PKG-GOVERNANCE-SECURITY",
        "objects": ["Permission definition"], "canonical": [],
        "owner": "Governance & Security", "sor": "Governance & Security permission registry",
        "targetPackage": "PKG-GOVERNANCE-SECURITY", "status": "LEGACY_OWNER",
        "migration": "CONTRACT_FIRST", "task": "ONE-A5-P1-16",
    },
    "sys_version": {
        "module": "UCore", "package": "PKG-UCORE", "objects": ["OperationalContext"],
        "canonical": ["OperationalContext"], "owner": "UCore", "sor": "UCore",
        "targetPackage": "PKG-UCORE", "status": "CORRECT_OWNER",
        "migration": "NO_MIGRATION", "task": "ONE-A5-P1-16",
    },
    "sys_menu": {
        "module": "UCore", "package": "PKG-UCORE", "objects": ["OperationalContext"],
        "canonical": ["OperationalContext"], "owner": "UCore", "sor": "UCore",
        "targetPackage": "PKG-UCORE", "status": "CORRECT_OWNER",
        "migration": "NO_MIGRATION", "task": "ONE-A5-P1-16",
    },
    "sys_version_menu": {
        "module": "UCore", "package": "PKG-UCORE", "objects": ["OperationalContext"],
        "canonical": ["OperationalContext"], "owner": "UCore", "sor": "UCore",
        "targetPackage": "PKG-UCORE", "status": "CORRECT_OWNER",
        "migration": "NO_MIGRATION", "task": "ONE-A5-P1-16",
    },
}


def special_store(
    source: str, line: int, symbol: str, physical: str, store_type: str,
    module: str, package: str, semantic: list[str], canonical: list[str],
    owner: str, sor: str, target_package: str, status: str, migration: str,
    task: str, role: str, notes: list[str],
) -> dict:
    return {
        "storeId": stable_id(store_type, physical),
        "storeType": store_type,
        "sourcePath": source,
        "line": line,
        "symbol": symbol,
        "physicalName": physical,
        "currentModule": module,
        "currentPackage": package,
        "currentSemanticObjects": semantic,
        "currentPersistenceRole": role,
        "canonicalObjects": canonical,
        "canonicalOwner": owner,
        "targetSystemOfRecord": sor,
        "targetPackage": target_package,
        "ownershipStatus": status,
        "migrationClass": migration,
        "compatibilityFacadeRequired": migration in {"READ_FACADE", "STRANGLER_MIGRATION", "OWNERSHIP_SPLIT", "RETIRE_AFTER_PARITY"},
        "dualReadAllowed": migration in {"READ_FACADE", "STRANGLER_MIGRATION", "DATA_COPY_AND_RECONCILE", "OWNERSHIP_SPLIT"},
        "dualWriteAllowed": False,
        "dataReconciliationRequired": migration in {"STRANGLER_MIGRATION", "DATA_COPY_AND_RECONCILE", "OWNERSHIP_SPLIT", "RETIRE_AFTER_PARITY"},
        "auditRequired": status != "CORRECT_OWNER" or migration != "NO_MIGRATION",
        "evidenceRequired": bool(set(canonical) & {"EvidenceRecord", "EvidenceRelationship", "HashAnchor", "AuditRecord"}),
        "retentionRequirement": "PRESERVE_UNTIL_RECONCILIATION_ROLLBACK_AND_RETIREMENT_GATES_PASS",
        "migrationPrerequisites": ["FROZEN_CONTRACT", "TARGET_PROVIDER_AVAILABLE", "IDENTIFIER_MAPPING_DEFINED"],
        "proposedMigrationTask": task,
        "rollbackRequirement": "PRESERVE_LEGACY_READ_PATH_AND_IMMUTABLE_SOURCE_UNTIL_ROLLBACK_WINDOW_CLOSES",
        "removalGate": "TARGET_PARITY_RECONCILIATION_STRICT_SCANNER_AND_APPROVAL",
        "scannerConfidence": "HIGH",
        "notes": notes,
    }


def table_entries(root: Path) -> tuple[list[dict], list[dict]]:
    src = root / "AN_VANTARIS_IBMS-backend/src"
    declarations: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
    unresolved: list[dict] = []
    for path in sorted(src.rglob("*.py")):
        relative = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except (SyntaxError, UnicodeDecodeError) as exc:
            unresolved.append({
                "storeId": stable_id("UNKNOWN", relative),
                "sourcePath": relative,
                "line": getattr(exc, "lineno", 1) or 1,
                "symbol": "",
                "evidence": "Python source could not be parsed conservatively.",
                "requiredReview": "Confirm whether the source declares a physical store.",
                "scannerConfidence": "LOW",
            })
            continue
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            for item in node.body:
                if not isinstance(item, (ast.Assign, ast.AnnAssign)):
                    continue
                targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                if not any(isinstance(target, ast.Name) and target.id == "__tablename__" for target in targets):
                    continue
                value = item.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    declarations[value.value].append((relative, item.lineno, node.name))
                else:
                    unresolved.append({
                        "storeId": stable_id("UNKNOWN", f"{relative}:{item.lineno}"),
                        "sourcePath": relative, "line": item.lineno, "symbol": node.name,
                        "evidence": "Dynamic __tablename__ declaration.",
                        "requiredReview": "Resolve physical table name without importing the backend.",
                        "scannerConfidence": "MEDIUM",
                    })
    stores: list[dict] = []
    for physical in sorted(declarations):
        refs = sorted(declarations[physical])
        source, line, symbol = refs[0]
        mapping = TABLE_MAP.get(physical)
        if not mapping:
            unresolved.append({
                "storeId": stable_id("UNKNOWN", physical),
                "sourcePath": source, "line": line, "symbol": symbol,
                "evidence": f"Explicit table {physical} has no frozen ownership mapping.",
                "requiredReview": "Assign canonical ownership before migration implementation.",
                "scannerConfidence": "HIGH",
            })
            continue
        stores.append(special_store(
            source, line, symbol, physical, "SQL_TABLE", mapping["module"], mapping["package"],
            sorted(set(mapping["objects"] + [ref[2] for ref in refs])), mapping["canonical"],
            mapping["owner"], mapping["sor"], mapping["targetPackage"], mapping["status"],
            mapping["migration"], mapping["task"], "AUTHORITATIVE_OR_LEGACY_RELATIONAL_PERSISTENCE",
            [
                "Explicit SQLAlchemy __tablename__ declaration.",
                "All model declarations for this physical table: " + ", ".join(f"{ref[0]}:{ref[2]}" for ref in refs),
                "Physical storage does not determine frozen semantic ownership.",
            ],
        ))
    return stores, unresolved


def build(root: Path) -> dict:
    stores, unresolved = table_entries(root)
    stores.extend([
        special_store(
            "AN_VANTARIS_IBMS-backend/src/reports/reports_audit_store.py", 20,
            "get_audit_store_path", "runtime/reports_audit/reports_audit.jsonl",
            "JSONL_LEDGER", "Reports", "PKG-REPORTS", ["AuditRecord"], ["AuditRecord"],
            "Governance & Security", "Governance & Security Audit Service",
            "PKG-GOVERNANCE-SECURITY", "LEGACY_OWNER", "DATA_COPY_AND_RECONCILE",
            "ONE-A5-P1-10", "LOCAL_AUDIT_READINESS_LEDGER",
            ["Local hash-chain JSONL is compatibility-only and not the target AuditRecord system of record."],
        ),
        special_store(
            "AN_VANTARIS_IBMS-backend/src/umms/umms_provider.py", 91,
            "_base_work_orders", "umms:_base_work_orders", "IN_MEMORY_STORE",
            "UMMS", "PKG-UMMS", ["WorkOrder", "MaintenanceFinding"],
            ["WorkOrder", "MaintenanceFinding"], "ONE Work Management / UMMS",
            "ONE Work Management for generic lifecycle; UMMS for maintenance extensions",
            "PKG-WORK-MANAGEMENT", "PLACEHOLDER", "STRANGLER_MIGRATION",
            "ONE-A5-P1-12", "READ_ONLY_MOCK_PROVIDER",
            ["mockData=true, readOnly=true, and DB persistence is explicitly absent."],
        ),
        special_store(
            "AN_VANTARIS_IBMS-backend/src/ucde/evidence_provider.py", 124,
            "_base_records", "ucde:_base_records", "IN_MEMORY_STORE",
            "UCDE", "PKG-UCDE", ["EvidenceRecord", "EvidenceRelationship", "HashAnchor"],
            ["EvidenceRecord", "EvidenceRelationship", "HashAnchor"],
            "Evidence Center / Evidence Center / Trust", "Evidence Center and Governance & Security / Trust",
            "PKG-EVIDENCE-CENTER", "PLACEHOLDER", "STRANGLER_MIGRATION",
            "ONE-A5-P1-14", "READ_ONLY_MOCK_PROVIDER",
            ["UCDE is the investigation workspace consumer; it is not the EvidenceRecord system of record."],
        ),
        special_store(
            "AN_VANTARIS_IBMS-backend/src/assets/assets_provider.py", 80,
            "_base_assets", "assets:_base_assets", "IN_MEMORY_STORE",
            "ONE Asset Graph", "PKG-ASSET-GRAPH", ["Asset", "Equipment"],
            ["Asset", "Equipment"], "ONE Asset Graph", "ONE Asset Graph",
            "PKG-ASSET-GRAPH", "PLACEHOLDER", "CONTRACT_FIRST",
            "ONE-A5-P1-07", "READ_ONLY_MOCK_PROVIDER",
            ["Correct semantic owner, but provider is placeholder data rather than a durable canonical store."],
        ),
        special_store(
            "AN_VANTARIS_IBMS-backend/src/uedge/uedge_provider.py", 51,
            "customer_setup_steps", "uedge:runtime_placeholder", "IN_MEMORY_STORE",
            "AN_VANTARIS_EDGE", "PKG-EDGE",
            ["GatewayRuntime", "ConnectorRuntime", "DiscoveryObservation"],
            ["GatewayRuntime", "ConnectorRuntime", "DiscoveryObservation"],
            "AN_VANTARIS_EDGE", "AN_VANTARIS_EDGE", "PKG-EDGE",
            "PLACEHOLDER", "CONTRACT_FIRST", "ONE-A5-P1-07",
            "READ_ONLY_RUNTIME_DIAGNOSTIC_PLACEHOLDER",
            ["EDGE owns runtime connectivity and discovery, not canonical Device or Point identity."],
        ),
        special_store(
            "AN_VANTARIS_IBMS-backend/src/data_modeling/csv_storage.py", 34,
            "CSVStorage", "data_modeling/device_code.csv", "LOCAL_FILESYSTEM",
            "Nexus AI", "PKG-NEXUS-AI", ["AITrace", "ModelMetadata"],
            ["AITrace", "ModelMetadata"], "Nexus AI / AI Model Hub",
            "Nexus AI request trace and AI Model Hub model metadata",
            "PKG-NEXUS-AI", "LOCAL_FALLBACK", "OWNERSHIP_SPLIT",
            "ONE-A5-P1-16", "LOCAL_MODELING_DATASET_STORE",
            ["Local per-device CSV persistence mixes request data and model-related concerns."],
        ),
        special_store(
            "AN_VANTARIS_ONE/registries/api-namespace-registry.v1.json", 298,
            "/api/v1/adapters/ufms", "UFMS_EXTERNAL_INTEGRATION_REFERENCE",
            "EXTERNAL_STORE_REFERENCE", "VANTARIS ONE UFMS Integration Boundary",
            "PKG-UFMS-INTEGRATION",
            ["InterpretedEvent", "Alarm", "Episode", "Problem", "FaultCase", "WorkOrderIntent"],
            ["InterpretedEvent", "Alarm", "Episode", "Problem", "FaultCase", "WorkOrderIntent"],
            "UFMS", "UFMS", "PKG-UFMS-INTEGRATION", "PLACEHOLDER",
            "CONTRACT_FIRST", "ONE-A5-P1-16", "EXTERNAL_PRODUCT_REFERENCE_ONLY",
            [
                "UFMS is external; no UFMS physical table is asserted or absorbed into ONE.",
                "LIVE_UFMS_VERIFICATION_REQUIRED for implementation endpoints, payloads, authentication, errors, versions, pagination, and delivery mode.",
            ],
        ),
    ])
    stores.sort(key=lambda row: row["storeId"])
    unresolved.sort(key=lambda row: row["storeId"])
    by_module = Counter(row["currentModule"] for row in stores)
    by_owner = Counter(row["canonicalOwner"] for row in stores)
    by_migration = Counter(row["migrationClass"] for row in stores)
    summary = {
        "totalStores": len(stores),
        "sqlTables": sum(row["storeType"] == "SQL_TABLE" for row in stores),
        "ormModels": sum(row["storeType"] == "ORM_MODEL" for row in stores),
        "jsonStores": sum(row["storeType"] == "JSON_FILE" for row in stores),
        "jsonlStores": sum(row["storeType"] == "JSONL_LEDGER" for row in stores),
        "localFilesystemStores": sum(row["storeType"] == "LOCAL_FILESYSTEM" for row in stores),
        "inMemoryStores": sum(row["storeType"] == "IN_MEMORY_STORE" for row in stores),
        "correctOwnerStores": sum(row["ownershipStatus"] == "CORRECT_OWNER" for row in stores),
        "legacyOwnerStores": sum(row["ownershipStatus"] == "LEGACY_OWNER" for row in stores),
        "mixedResponsibilityStores": sum(row["ownershipStatus"] == "MIXED_RESPONSIBILITY" for row in stores),
        "placeholderStores": sum(row["ownershipStatus"] == "PLACEHOLDER" for row in stores),
        "unresolvedStores": len(unresolved),
        "storesByCurrentModule": dict(sorted(by_module.items())),
        "storesByCanonicalOwner": dict(sorted(by_owner.items())),
        "storesByMigrationClass": dict(sorted(by_migration.items())),
    }
    return {
        "registryName": "VANTARIS ONE Legacy Physical Store Owner Map",
        "registryVersion": "1.0.0",
        "authority": "ONE-A5-P0-08",
        "status": "FROZEN_LEGACY_STORE_BASELINE",
        "generatedAtPolicy": "STATIC_ARCHITECTURE_BASELINE",
        "extractionPolicy": {
            "mode": "PYTHON_AST_AND_CONSERVATIVE_STATIC_TEXT",
            "backendImportExecution": False,
            "databaseConnection": False,
            "modelExecution": False,
            "physicalTablePolicy": "ONLY_EXPLICIT_TABLENAME_DECLARATIONS",
            "duplicatePhysicalNamePolicy": "ONE_STORE_WITH_ALL_MODEL_DECLARATIONS_NOTED",
            "unresolvedPolicy": "RETAIN_EXPLICITLY",
        },
        "summary": summary,
        "physicalStores": stores,
        "unresolvedStores": unresolved,
    }


def serialize(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=["json"], default="json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    value = build(root)
    rendered = serialize(value)
    output = args.output
    if output and not output.is_absolute():
        output = root / output
    check_path = output or root / "AN_VANTARIS_ONE/registries/legacy-table-owner-map.v1.json"
    if args.check:
        if not check_path.is_file() or check_path.read_text(encoding="utf-8") != rendered:
            print(f"legacy owner map differs: {check_path}", file=sys.stderr)
            return 1
        print("ONE_LEGACY_OWNERSHIP_INVENTORY_CHECK_PASS")
        return 0
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
