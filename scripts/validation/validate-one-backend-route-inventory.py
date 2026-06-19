#!/usr/bin/env python3
"""Validate the committed VANTARIS ONE backend route inventory."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "AN_VANTARIS_ONE/registries/backend-route-inventory.v1.json"
BUILDER = ROOT / "scripts/validation/build-one-backend-route-inventory.py"
PACKAGES = ROOT / "AN_VANTARIS_ONE/registries/package-registry.v1.json"
APIS = ROOT / "AN_VANTARIS_ONE/registries/api-namespace-registry.v1.json"
PERMISSIONS = ROOT / "AN_VANTARIS_ONE/registries/permission-registry.v1.json"

ALLOWED = {
    "runtimeClass": {"PRODUCTION", "LEGACY", "TEST_ONLY", "UNKNOWN"},
    "namespaceStatus": {"TARGET_NAMESPACE", "LEGACY_COMPATIBILITY", "NAMESPACE_DRIFT", "UNRESOLVED"},
    "operationClass": {"READ", "WRITE", "CONTROL", "INTAKE", "EXPORT", "AUTH", "HEALTH", "STREAM", "MIXED", "UNKNOWN"},
    "authenticationClass": {"AUTHENTICATED", "EXPLICITLY_PUBLIC", "UNCLASSIFIED", "INHERITED_UNKNOWN"},
    "permissionClass": {"ACTION_GUARDED", "PERMISSION_GUARDED", "AUTH_ONLY", "UNGUARDED", "NOT_APPLICABLE", "UNRESOLVED"},
    "tenantScopeClass": {"TENANT_REQUIRED", "TENANT_OPTIONAL", "GLOBAL_PLATFORM", "UNDECLARED", "NOT_APPLICABLE"},
    "siteScopeClass": {"SITE_REQUIRED", "SITE_OPTIONAL", "TENANT_LEVEL", "GLOBAL_PLATFORM", "UNDECLARED", "NOT_APPLICABLE"},
    "packageEnforcementClass": {"DECLARED", "INFERRED_ONLY", "NOT_DECLARED", "NOT_APPLICABLE", "UNRESOLVED"},
    "auditClass": {"REQUIRED_DECLARED", "REQUIRED_NOT_DECLARED", "OPTIONAL", "NOT_APPLICABLE", "UNRESOLVED"},
    "idempotencyClass": {"REQUIRED_DECLARED", "REQUIRED_NOT_DECLARED", "NOT_REQUIRED", "NOT_APPLICABLE", "UNRESOLVED"},
    "publicExposureClass": {"PUBLIC_SAFE", "PUBLIC_SENSITIVE", "PROTECTED", "UNCLASSIFIED"},
    "legacyStatus": {"CURRENT_TARGET", "LEGACY_KEEP", "LEGACY_COMPATIBILITY_REQUIRED", "LEGACY_MIGRATE", "REVIEW_REQUIRED"},
    "scannerConfidence": {"HIGH", "MEDIUM", "LOW"},
}


def main() -> int:
    errors = []
    try:
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        packages = json.loads(PACKAGES.read_text(encoding="utf-8"))
        apis = json.loads(APIS.read_text(encoding="utf-8"))
        permissions = json.loads(PERMISSIONS.read_text(encoding="utf-8"))
    except Exception as exc:
        print("[ONE BACKEND ROUTE INVENTORY VALIDATION]")
        print(f"FAIL: {exc}")
        print("ONE_BACKEND_ROUTE_INVENTORY_FAIL")
        return 1

    required_top = {
        "registryName", "registryVersion", "authority", "status", "generatedAtPolicy",
        "sourceRoot", "extractionPolicy", "summary", "routes", "unresolvedRegistrations",
    }
    if not required_top.issubset(inventory):
        errors.append("missing required top-level fields")
    if inventory.get("registryName") != "VANTARIS ONE Backend Route Inventory":
        errors.append("invalid registryName")
    if inventory.get("registryVersion") != "1.0.0" or inventory.get("authority") != "ONE-A5-P0-04":
        errors.append("invalid registry version or authority")
    if inventory.get("status") != "FROZEN_ROUTE_CLASSIFICATION_BASELINE":
        errors.append("invalid inventory status")
    if inventory.get("generatedAtPolicy") != "STATIC_ARCHITECTURE_BASELINE":
        errors.append("invalid generatedAtPolicy")
    if inventory.get("sourceRoot") != "AN_VANTARIS_IBMS-backend/src":
        errors.append("invalid sourceRoot")

    package_ids = {row["packageId"] for row in packages["packages"]}
    api_names = {row["namespace"] for row in apis["apiNamespaces"]}
    permission_names = {row["permission"] for row in permissions["permissions"]}
    routes = inventory.get("routes", [])
    route_ids = [row.get("routeId") for row in routes]
    if len(route_ids) != len(set(route_ids)):
        errors.append("duplicate routeId")
    required_route_fields = {
        "routeId", "sourcePath", "line", "symbol", "blueprintName", "blueprintPrefix",
        "routePath", "fullPath", "methods", "runtimeClass", "owningModule", "packageId",
        "currentNamespace", "targetNamespace", "namespaceStatus", "operationClass",
        "authenticationClass", "authenticationEvidence", "permissionClass",
        "declaredPermissions", "permissionEvidence", "tenantScopeClass", "siteScopeClass",
        "packageEnforcementClass", "auditClass", "idempotencyClass", "publicExposureClass",
        "legacyStatus", "compatibilityRequirement", "remediationWorkstream", "proposedTaskId",
        "scannerConfidence", "notes",
    }
    for row in routes:
        rid = row.get("routeId")
        if set(row) != required_route_fields:
            errors.append(f"{rid}: invalid route structure")
        source_path = row.get("sourcePath")
        if not isinstance(source_path, str) or source_path.startswith("/") or "/Users/" in source_path:
            errors.append(f"{rid}: sourcePath must be repository-relative")
        methods = row.get("methods")
        if not isinstance(methods, list) or not methods or methods != sorted(set(methods)) or any(method != method.upper() for method in methods):
            errors.append(f"{rid}: methods must be non-empty sorted uppercase values")
        for field, values in ALLOWED.items():
            if row.get(field) not in values:
                errors.append(f"{rid}: invalid {field}")
        if row.get("packageId") and row["packageId"] not in package_ids:
            errors.append(f"{rid}: unknown packageId")
        if row.get("targetNamespace") and row["targetNamespace"] not in api_names:
            errors.append(f"{rid}: unknown targetNamespace")
        unknown_permissions = set(row.get("declaredPermissions", [])) - permission_names
        if unknown_permissions:
            errors.append(f"{rid}: unknown declared permissions")
        if row.get("operationClass") in {"WRITE", "CONTROL", "INTAKE", "EXPORT", "MIXED"} and row.get("auditClass") not in {"REQUIRED_DECLARED", "REQUIRED_NOT_DECLARED", "UNRESOLVED"}:
            errors.append(f"{rid}: invalid mutation audit classification")
        if row.get("operationClass") in {"INTAKE", "CONTROL"} and "POST" in row.get("methods", []) and row.get("idempotencyClass") not in {"REQUIRED_DECLARED", "REQUIRED_NOT_DECLARED", "UNRESOLVED"}:
            errors.append(f"{rid}: invalid intake/control idempotency classification")
        if row.get("authenticationClass") not in ALLOWED["authenticationClass"]:
            errors.append(f"{rid}: missing authentication classification")
        if row.get("runtimeClass") != "TEST_ONLY" and row.get("publicExposureClass") != "PUBLIC_SAFE" and row.get("packageEnforcementClass") not in {"DECLARED", "INFERRED_ONLY", "NOT_DECLARED", "UNRESOLVED"}:
            errors.append(f"{rid}: invalid business package classification")
        if row.get("line") is not None and (not isinstance(row["line"], int) or row["line"] <= 0):
            errors.append(f"{rid}: invalid line")

    unresolved = inventory.get("unresolvedRegistrations", [])
    required_unresolved = {"sourcePath", "line", "symbol", "unresolvedType", "evidence", "requiredReview", "scannerConfidence"}
    for row in unresolved:
        if set(row) != required_unresolved:
            errors.append("invalid unresolved registration structure")
        if row.get("line") is not None and (not isinstance(row["line"], int) or row["line"] <= 0):
            errors.append("invalid unresolved line")

    summary = inventory.get("summary", {})
    calculated = Counter()
    by_module = Counter()
    by_package = Counter()
    by_namespace = Counter()
    for row in routes:
        calculated["totalRoutes"] += 1
        calculated[{"PRODUCTION": "productionRoutes", "LEGACY": "legacyRoutes", "TEST_ONLY": "testOnlyRoutes", "UNKNOWN": "unresolvedRoutes"}[row["runtimeClass"]]] += 1
        calculated[{"AUTHENTICATED": "authenticatedRoutes", "EXPLICITLY_PUBLIC": "explicitlyPublicRoutes", "UNCLASSIFIED": "unclassifiedAuthRoutes", "INHERITED_UNKNOWN": "unclassifiedAuthRoutes"}[row["authenticationClass"]]] += 1
        if row["permissionClass"] in {"ACTION_GUARDED", "PERMISSION_GUARDED"}:
            calculated["permissionGuardedRoutes"] += 1
        elif row["permissionClass"] == "AUTH_ONLY":
            calculated["authOnlyRoutes"] += 1
        elif row["permissionClass"] == "UNGUARDED":
            calculated["unguardedRoutes"] += 1
        if row["operationClass"] in {"WRITE", "CONTROL", "INTAKE", "EXPORT", "MIXED"}:
            calculated["mutationRoutes"] += 1
            if row["permissionClass"] not in {"ACTION_GUARDED", "PERMISSION_GUARDED"}:
                calculated["mutationWithoutActionGuard"] += 1
        if row["auditClass"] == "REQUIRED_NOT_DECLARED":
            calculated["auditRequiredNotDeclared"] += 1
        if row["idempotencyClass"] == "REQUIRED_NOT_DECLARED":
            calculated["idempotencyRequiredNotDeclared"] += 1
        calculated[{"DECLARED": "packageDeclaredRoutes", "INFERRED_ONLY": "packageInferredRoutes", "NOT_DECLARED": "packageNotDeclaredRoutes", "NOT_APPLICABLE": "packageNotDeclaredRoutes", "UNRESOLVED": "packageNotDeclaredRoutes"}[row["packageEnforcementClass"]]] += 1
        calculated[{"TARGET_NAMESPACE": "targetNamespaceRoutes", "LEGACY_COMPATIBILITY": "legacyCompatibilityRoutes", "NAMESPACE_DRIFT": "namespaceDriftRoutes", "UNRESOLVED": "namespaceDriftRoutes"}[row["namespaceStatus"]]] += 1
        by_module[row["owningModule"]] += 1
        by_package[row["packageId"] or "UNRESOLVED"] += 1
        by_namespace[row["currentNamespace"]] += 1
    calculated["unresolvedRoutes"] = len(unresolved)
    for key, value in calculated.items():
        if summary.get(key) != value:
            errors.append(f"summary mismatch: {key}")
    if summary.get("routesByModule") != dict(sorted(by_module.items())):
        errors.append("summary mismatch: routesByModule")
    if summary.get("routesByPackage") != dict(sorted(by_package.items())):
        errors.append("summary mismatch: routesByPackage")
    if summary.get("routesByCurrentNamespace") != dict(sorted(by_namespace.items())):
        errors.append("summary mismatch: routesByCurrentNamespace")

    serialized = json.dumps(inventory, sort_keys=True)
    if re.search(r"\b20\d{2}-\d{2}-\d{2}\b", serialized) or "/Users/" in serialized:
        errors.append("timestamp or absolute user path found")
    if "http://" in serialized or "https://" in serialized or "localhost" in serialized:
        errors.append("live/environment endpoint found")

    completed = subprocess.run(
        [sys.executable, str(BUILDER), "--root", str(ROOT), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    deterministic_ok = completed.returncode == 0 and INVENTORY.read_text(encoding="utf-8") == completed.stdout
    if not deterministic_ok:
        errors.append("committed inventory differs from deterministic builder output")

    checks = [
        ("JSON structure", not any("structure" in item or "top-level" in item or "registryName" in item for item in errors)),
        ("Route IDs", not any("routeId" in item for item in errors)),
        ("Package references", not any("packageId" in item for item in errors)),
        ("Namespace references", not any("targetNamespace" in item for item in errors)),
        ("Permission references", not any("permission" in item for item in errors)),
        ("Authentication classification", not any("authentication" in item for item in errors)),
        ("Audit classification", not any("audit classification" in item for item in errors)),
        ("Idempotency classification", not any("idempotency" in item for item in errors)),
        ("Deterministic extraction", deterministic_ok),
        ("Unresolved coverage", not any("unresolved" in item for item in errors)),
    ]
    print("[ONE BACKEND ROUTE INVENTORY VALIDATION]")
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_BACKEND_ROUTE_INVENTORY_FAIL")
        return 1
    print("ONE_BACKEND_ROUTE_INVENTORY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
