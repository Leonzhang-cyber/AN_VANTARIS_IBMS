#!/usr/bin/env python3
"""Validate VANTARIS ONE package-route enforcement metadata."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "AN_VANTARIS_ONE/registries/frontend-route-inventory.v1.json"
ENFORCEMENT = ROOT / "AN_VANTARIS_ONE/registries/package-route-enforcement.v1.json"
PACKAGES = ROOT / "AN_VANTARIS_ONE/registries/package-registry.v1.json"
PERMISSIONS = ROOT / "AN_VANTARIS_ONE/registries/permission-registry.v1.json"
APIS = ROOT / "AN_VANTARIS_ONE/registries/api-namespace-registry.v1.json"
BUILDER = ROOT / "scripts/validation/build-one-frontend-route-inventory.py"

RUNTIME_CLASSES = {"PRODUCTION", "LEGACY", "TEST_ONLY", "PLACEHOLDER", "UNKNOWN"}
GUARD_CLASSES = {
    "AUTHENTICATION_ONLY", "PERMISSION_AWARE", "PACKAGE_AWARE",
    "FULL_POLICY", "NO_GUARD", "INHERITED_UNKNOWN",
}
ACCESS_CLASSES = {
    "BUSINESS_ROUTE", "ADMIN_ROUTE", "DIAGNOSTIC_ROUTE", "LOCK_PAGE",
    "STATUS_ROUTE", "PUBLIC_ROUTE", "TEST_ONLY", "DENY",
}
VISIBILITY_CLASSES = {
    "VISIBLE_WHEN_AUTHORIZED", "VISIBLE_AS_LOCKED", "VISIBLE_FOR_DIAGNOSTICS",
    "ADMIN_ONLY", "HIDDEN_WHEN_DISABLED", "NOT_IN_LEFT_NAVIGATION",
    "REMOVE_LATER", "REVIEW_REQUIRED",
}
DIRECT_URL_POLICIES = {
    "ALLOW_WHEN_AUTHORIZED", "LOCK_PAGE_WHEN_UNLICENSED",
    "STATUS_PAGE_WHEN_UNAVAILABLE", "ADMIN_DIAGNOSTICS_ONLY", "DENY", "TEST_ONLY",
}
IMPLEMENTATION_STATUSES = {
    "ALREADY_COMPLIANT", "AUTH_GUARD_REQUIRED", "PERMISSION_METADATA_REQUIRED",
    "PACKAGE_METADATA_REQUIRED", "DIRECT_URL_ENFORCEMENT_REQUIRED",
    "BACKEND_POLICY_DEPENDENCY_REQUIRED", "MULTIPLE_CONTROLS_REQUIRED",
    "NON_PRODUCTION", "REVIEW_REQUIRED",
}
REVIEW_TYPES = {
    "ROUTE_PACKAGE_AMBIGUITY", "MENU_ROUTE_MISMATCH", "MISSING_PERMISSION",
    "MULTI_PACKAGE_PAGE", "HEALTH_POLICY_AMBIGUITY", "LEGACY_ROUTE_RETIREMENT",
    "STATIC_MENU_FALLBACK", "DYNAMIC_ROUTE", "BACKEND_DEPENDENCY_UNKNOWN",
}
ALLOWED_LOCK_METADATA = {
    "PACKAGE_DISPLAY_NAME", "INSTALLATION_STATUS", "ENTITLEMENT_STATUS_CATEGORY",
    "ENABLED_STATUS", "COMPATIBILITY_CATEGORY", "HIGH_LEVEL_HEALTH_CATEGORY",
    "REQUIRED_ADMINISTRATIVE_NEXT_ACTION", "SUPPORT_REFERENCE",
}


def load(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name}: {exc}")
        return {}


def inventory_summary(routes: list[dict], menus: list[dict]) -> dict:
    route_package = Counter(row["targetPackageId"] or "UNRESOLVED" for row in routes)
    route_owner = Counter(row["owningModule"] for row in routes)
    route_access = Counter(row["targetAccessClass"] for row in routes)
    menu_package = Counter(row["packageId"] or "UNRESOLVED" for row in menus)
    return {
        "routes": {
            "totalRoutes": len(routes),
            "productionRoutes": sum(row["runtimeClass"] == "PRODUCTION" for row in routes),
            "legacyRoutes": sum(row["runtimeClass"] == "LEGACY" for row in routes),
            "placeholderRoutes": sum(row["runtimeClass"] == "PLACEHOLDER" for row in routes),
            "testOnlyRoutes": sum(row["runtimeClass"] == "TEST_ONLY" for row in routes),
            "routesWithCurrentAuthGuard": sum(row["currentGuardClass"] in {"AUTHENTICATION_ONLY", "PERMISSION_AWARE", "PACKAGE_AWARE", "FULL_POLICY"} for row in routes),
            "routesWithCurrentPermissionMetadata": sum(bool(row["currentPermissionMetadata"]) for row in routes),
            "routesWithCurrentPackageMetadata": sum(bool(row["currentPackageId"]) for row in routes),
            "routesCurrentlyDirectAddressable": sum(row["directUrlCurrentlyAddressable"] for row in routes),
            "routesRequiringPackageMetadata": sum(not row["currentPackageId"] and row["targetAccessClass"] not in {"PUBLIC_ROUTE", "STATUS_ROUTE"} for row in routes),
            "routesRequiringPermissionMetadata": sum(not row["currentPermissionMetadata"] and bool(row["targetPermissions"]) for row in routes),
            "routesRequiringDirectUrlEnforcement": sum(row["directUrlCurrentlyAddressable"] and row["targetAccessClass"] not in {"PUBLIC_ROUTE", "STATUS_ROUTE"} for row in routes),
            "routesRequiringMultipleControls": sum(not row["currentPackageId"] and not row["currentPermissionMetadata"] and bool(row["targetPermissions"]) for row in routes),
            "routesByPackage": dict(sorted(route_package.items())),
            "routesByOwningModule": dict(sorted(route_owner.items())),
            "routesByTargetAccessClass": dict(sorted(route_access.items())),
        },
        "menus": {
            "totalMenuEntries": len(menus),
            "staticFallbackEntries": sum(row["staticFallback"] for row in menus),
            "entriesWithRoleMetadata": sum(bool(row["currentRoleVisibility"]) for row in menus),
            "entriesWithPermissionMetadata": sum(bool(row["currentPermissionMetadata"]) for row in menus),
            "entriesWithPackageMetadata": sum(bool(row["packageId"]) for row in menus),
            "l1Entries": sum(bool(row["l1"]) for row in menus),
            "l2Entries": sum(bool(row["l2"]) for row in menus),
            "l3EntriesIncorrectlyInLeftNavigation": sum(bool(row["targetL3Workspace"]) for row in menus),
            "entriesRequiringMigration": sum(row["legacyStatus"] in {"LEGACY_MIGRATE", "LEGACY_COMPATIBILITY_REQUIRED", "REMOVE_LATER", "REVIEW_REQUIRED"} for row in menus),
            "entriesByPackage": dict(sorted(menu_package.items())),
        },
    }


def enforcement_summary(doc: dict) -> dict:
    rows = doc.get("frontendRoutePolicies", [])
    statuses = Counter(row.get("implementationStatus") for row in rows)
    return {
        "packagePolicyCount": len(doc.get("packagePolicies", [])),
        "backendNamespacePolicyCount": len(doc.get("backendNamespacePolicies", [])),
        "frontendRoutePolicyCount": len(rows),
        "lockPagePolicyCount": len(doc.get("lockPagePolicies", [])),
        "diagnosticPolicyCount": len(doc.get("diagnosticPolicies", [])),
        "compatibilityMappingCount": len(doc.get("compatibilityPolicies", [])),
        "reviewQueueCount": len(doc.get("reviewQueue", [])),
        "currentlyCompliantRoutes": statuses["ALREADY_COMPLIANT"],
        "metadataOnlyRoutes": sum(row.get("implementationStatus") in {
            "PERMISSION_METADATA_REQUIRED", "PACKAGE_METADATA_REQUIRED",
            "BACKEND_POLICY_DEPENDENCY_REQUIRED",
        } for row in rows),
        "runtimeEnforcementRequiredRoutes": sum(row.get("implementationStatus") not in {
            "ALREADY_COMPLIANT", "NON_PRODUCTION",
        } for row in rows),
    }


def main() -> int:
    errors: list[str] = []
    for path in (FRONTEND, ENFORCEMENT):
        if not path.is_file():
            errors.append(f"missing registry: {path.name}")
    front = load(FRONTEND, errors) if FRONTEND.is_file() else {}
    enforcement = load(ENFORCEMENT, errors) if ENFORCEMENT.is_file() else {}
    package_doc = load(PACKAGES, errors)
    permission_doc = load(PERMISSIONS, errors)
    api_doc = load(APIS, errors)

    front_top = {
        "registryName", "registryVersion", "authority", "status", "generatedAtPolicy",
        "sourceRoots", "extractionPolicy", "summary", "routes", "menuEntries",
        "unresolvedDeclarations",
    }
    enforcement_top = {
        "registryName", "registryVersion", "authority", "status", "generatedAtPolicy",
        "enforcementPrinciples", "packageStateSemantics", "healthAccessSemantics",
        "frontendRoutePolicies", "backendNamespacePolicies", "packagePolicies",
        "lockPagePolicies", "diagnosticPolicies", "compatibilityPolicies",
        "reviewQueue", "summary",
    }
    if set(front) != front_top:
        errors.append("frontend inventory invalid top-level fields")
    if set(enforcement) != enforcement_top:
        errors.append("enforcement registry invalid top-level fields")
    fixed_front = {
        "registryName": "VANTARIS ONE Frontend Route Inventory",
        "registryVersion": "1.0.0",
        "authority": "ONE-A5-P0-06",
        "status": "FROZEN_FRONTEND_ROUTE_BASELINE",
        "generatedAtPolicy": "STATIC_ARCHITECTURE_BASELINE",
    }
    fixed_enforcement = {
        "registryName": "VANTARIS ONE Package Route Enforcement Registry",
        "registryVersion": "1.0.0",
        "authority": "ONE-A5-P0-06",
        "status": "FROZEN_FOR_PACKAGE_ENFORCEMENT_IMPLEMENTATION",
        "generatedAtPolicy": "STATIC_ARCHITECTURE_BASELINE",
    }
    for field, value in fixed_front.items():
        if front.get(field) != value:
            errors.append(f"frontend inventory invalid {field}")
    for field, value in fixed_enforcement.items():
        if enforcement.get(field) != value:
            errors.append(f"enforcement registry invalid {field}")

    package_ids = {row.get("packageId") for row in package_doc.get("packages", [])}
    package_by_id = {row.get("packageId"): row for row in package_doc.get("packages", [])}
    permission_ids = {row.get("permission") for row in permission_doc.get("permissions", [])}
    namespaces = {row.get("namespace") for row in api_doc.get("apiNamespaces", [])}

    route_fields = {
        "frontendRouteId", "sourcePath", "line", "symbol", "routePath", "routeName",
        "component", "parentRoute", "runtimeClass", "currentPackageId",
        "targetPackageId", "owningModule", "currentPermissionMetadata",
        "targetPermissions", "currentEntitlementMetadata",
        "currentPackageEnabledMetadata", "currentHealthMetadata",
        "directUrlCurrentlyAddressable", "currentGuardClass", "currentMenuPresence",
        "targetMenuPresence", "targetAccessClass", "backendApiDependencies",
        "legacyStatus", "compatibilityRequirement", "remediationWorkstream",
        "proposedTaskId", "scannerConfidence", "notes",
    }
    menu_fields = {
        "menuEntryId", "sourcePath", "line", "label", "l1", "l2",
        "targetL3Workspace", "routePath", "packageId", "owningModule",
        "currentRoleVisibility", "currentPermissionMetadata",
        "currentEntitlementMetadata", "currentEnabledMetadata", "currentHealthMetadata",
        "staticFallback", "currentVisibilityClass", "targetVisibilityClass",
        "legacyStatus", "scannerConfidence", "notes",
    }
    routes = front.get("routes", [])
    menus = front.get("menuEntries", [])
    route_ids = [row.get("frontendRouteId") for row in routes]
    menu_ids = [row.get("menuEntryId") for row in menus]
    if len(route_ids) != len(set(route_ids)):
        errors.append("duplicate frontend route ID")
    if len(menu_ids) != len(set(menu_ids)):
        errors.append("duplicate menu entry ID")
    if route_ids != sorted(route_ids) or menu_ids != sorted(menu_ids):
        errors.append("frontend inventories are not deterministically sorted")
    for row in routes:
        rid = row.get("frontendRouteId")
        if set(row) != route_fields:
            errors.append(f"{rid}: invalid frontend route structure")
        if row.get("runtimeClass") not in RUNTIME_CLASSES:
            errors.append(f"{rid}: invalid runtime class")
        if row.get("currentGuardClass") not in GUARD_CLASSES:
            errors.append(f"{rid}: invalid current guard class")
        if row.get("targetAccessClass") not in ACCESS_CLASSES:
            errors.append(f"{rid}: invalid target access class")
        if row.get("targetPackageId") not in package_ids:
            errors.append(f"{rid}: unknown target package")
        if set(row.get("targetPermissions", [])) - permission_ids:
            errors.append(f"{rid}: unknown target permission")
        if set(row.get("backendApiDependencies", [])) - namespaces:
            errors.append(f"{rid}: unknown backend namespace dependency")
        if row.get("runtimeClass") == "TEST_ONLY" and row.get("targetAccessClass") != "TEST_ONLY":
            errors.append(f"{rid}: test route is not TEST_ONLY")
    for row in menus:
        mid = row.get("menuEntryId")
        if set(row) != menu_fields:
            errors.append(f"{mid}: invalid menu structure")
        if row.get("packageId") not in package_ids:
            errors.append(f"{mid}: unknown menu package")
        if row.get("targetVisibilityClass") not in VISIBILITY_CLASSES:
            errors.append(f"{mid}: invalid target visibility")
        if row.get("targetL3Workspace"):
            errors.append(f"{mid}: L3 incorrectly represented in left navigation")
    if front.get("summary") != inventory_summary(routes, menus):
        errors.append("frontend route or menu summary mismatch")

    route_policy_fields = {
        "frontendRouteId", "routePath", "packageId", "owningModule",
        "targetAccessClass", "authenticationRequired", "requiredPermissions",
        "entitlementRequired", "installedRequired", "enabledRequired",
        "compatibleRequired", "allowedHealthStates", "tenantScopeRequired",
        "siteScopeRequired", "directUrlPolicy", "menuPolicy", "lockPagePolicy",
        "diagnosticFallback", "backendApiPolicyReferences", "auditPolicy",
        "compatibilityStage", "implementationStatus", "remediationWorkstream",
        "proposedImplementationTask", "reviewReason", "notes",
    }
    route_policies = enforcement.get("frontendRoutePolicies", [])
    policy_ids = [row.get("frontendRouteId") for row in route_policies]
    if len(policy_ids) != len(set(policy_ids)) or set(policy_ids) != set(route_ids):
        errors.append("frontend route enforcement policy coverage mismatch")
    if policy_ids != sorted(policy_ids):
        errors.append("frontend route policies are not deterministically sorted")
    for row in route_policies:
        rid = row.get("frontendRouteId")
        if set(row) != route_policy_fields:
            errors.append(f"{rid}: invalid frontend policy structure")
        if row.get("packageId") not in package_ids:
            errors.append(f"{rid}: unknown policy package")
        if set(row.get("requiredPermissions", [])) - permission_ids:
            errors.append(f"{rid}: unknown policy permission")
        if set(row.get("backendApiPolicyReferences", [])) - namespaces:
            errors.append(f"{rid}: unknown policy backend namespace")
        if row.get("directUrlPolicy") not in DIRECT_URL_POLICIES or not row.get("menuPolicy"):
            errors.append(f"{rid}: direct URL or menu policy missing")
        if row.get("implementationStatus") not in IMPLEMENTATION_STATUSES:
            errors.append(f"{rid}: invalid implementation status")
        package = package_by_id.get(row.get("packageId"), {})
        business = row.get("targetAccessClass") in {"BUSINESS_ROUTE", "ADMIN_ROUTE", "DIAGNOSTIC_ROUTE"}
        if business and package and not package.get("mandatory"):
            if not all(row.get(field) is True for field in ("entitlementRequired", "installedRequired", "enabledRequired")):
                errors.append(f"{rid}: optional package route lacks entitlement/install/enablement")
        if business and package and package.get("mandatory"):
            if not row.get("installedRequired") or not row.get("enabledRequired"):
                errors.append(f"{rid}: mandatory package route lacks install/enablement")
        if row.get("targetAccessClass") == "TEST_ONLY" and row.get("implementationStatus") != "NON_PRODUCTION":
            errors.append(f"{rid}: test route enforcement is not non-production")
        if row.get("implementationStatus") == "ALREADY_COMPLIANT":
            if not any("Missing controls: NONE" in note for note in row.get("notes", [])):
                errors.append(f"{rid}: current enforcement falsely reported")
        if not any("not implemented" in note for note in row.get("notes", [])):
            errors.append(f"{rid}: runtime honesty note missing")

    backend_fields = {
        "namespace", "packageId", "owningModule", "businessApi",
        "entitlementRequired", "installedRequired", "enabledRequired",
        "compatibleRequired", "allowedHealthStates", "diagnosticOnlyOperations",
        "publicOperations", "denialCodes", "auditRequired", "backendGuardRequired",
        "serviceIdentityAllowed", "currentRuntimeState", "implementationStatus",
    }
    backend_policies = enforcement.get("backendNamespacePolicies", [])
    backend_names = [row.get("namespace") for row in backend_policies]
    if len(backend_names) != len(set(backend_names)) or set(backend_names) != namespaces:
        errors.append("backend namespace policy coverage mismatch")
    if backend_names != sorted(backend_names):
        errors.append("backend namespace policies are not deterministically sorted")
    for row in backend_policies:
        if set(row) != backend_fields:
            errors.append(f"{row.get('namespace')}: invalid backend namespace policy structure")
        if row.get("packageId") not in package_ids:
            errors.append(f"{row.get('namespace')}: unknown backend package")
        package = package_by_id.get(row.get("packageId"), {})
        if row.get("businessApi") and package and not package.get("mandatory"):
            if not all(row.get(field) is True for field in ("entitlementRequired", "installedRequired", "enabledRequired")):
                errors.append(f"{row.get('namespace')}: optional backend policy incomplete")
        if row.get("businessApi") and package and package.get("mandatory"):
            if not row.get("installedRequired") or not row.get("enabledRequired"):
                errors.append(f"{row.get('namespace')}: mandatory backend policy incomplete")
        if row.get("implementationStatus") != "RUNTIME_ENFORCEMENT_REQUIRED":
            errors.append(f"{row.get('namespace')}: backend runtime honesty invalid")

    package_fields = {
        "packageId", "packageClass", "mandatory", "entitlementRequired",
        "installationRequired", "enablementRequired", "compatibilityRequired",
        "healthRequiredForWrites", "frontendRoutes", "backendNamespaces",
        "lockPageRoute", "statusRoute", "diagnosticRoutes", "adminRoutes",
        "defaultMenuBehavior", "defaultDirectUrlBehavior", "defaultApiBehavior",
        "dependencyFailureBehavior", "currentImplementation", "targetImplementation",
        "implementationStatus", "validationGate",
    }
    package_policies = enforcement.get("packagePolicies", [])
    package_policy_ids = [row.get("packageId") for row in package_policies]
    if len(package_policy_ids) != len(set(package_policy_ids)) or set(package_policy_ids) != package_ids:
        errors.append("package policy coverage mismatch")
    if package_policy_ids != sorted(package_policy_ids):
        errors.append("package policies are not deterministically sorted")
    for row in package_policies:
        pid = row.get("packageId")
        if set(row) != package_fields:
            errors.append(f"{pid}: invalid package policy structure")
        source = package_by_id.get(pid, {})
        if source and not source.get("mandatory"):
            if not row.get("entitlementRequired"):
                errors.append(f"{pid}: optional package entitlement missing")
        if pid not in {"PKG-CONTRACTS", "PKG-DB"}:
            if not row.get("installationRequired") or not row.get("enablementRequired"):
                errors.append(f"{pid}: package install/enablement missing")
        if pid == "PKG-CONTRACTS":
            if row.get("frontendRoutes") or row.get("backendNamespaces") or row.get("defaultApiBehavior") != "NO_PUBLIC_BUSINESS_API":
                errors.append("PKG-CONTRACTS must have no runtime business route")
        if pid == "PKG-DB" and row.get("frontendRoutes"):
            errors.append("PKG-DB must have no frontend business route")
        if pid == "PKG-UFMS-INTEGRATION":
            target = row.get("targetImplementation", "")
            if not row.get("compatibilityRequired") or "DOES_NOT_OWN_UFMS_RUNTIME" not in target:
                errors.append("PKG-UFMS-INTEGRATION external boundary policy invalid")

    states = enforcement.get("packageStateSemantics", [])
    state_ids = [row.get("stateId") for row in states]
    expected_states = {"installed", "entitled", "enabled", "visible", "healthy", "compatible", "upgradeRequired"}
    if set(state_ids) != expected_states or len(state_ids) != len(expected_states):
        errors.append("package state dimensions are not independent and complete")
    state_fields = {
        "stateId", "sourceOfTruth", "allowedTransitions", "authoritativeProvider",
        "frontendUse", "backendUse", "auditRequired", "failureCode",
    }
    if any(set(row) != state_fields for row in states):
        errors.append("package state structure invalid")

    health_rows = enforcement.get("healthAccessSemantics", [])
    health_ids = {row.get("healthState") for row in health_rows}
    expected_health = {
        "HEALTHY", "DEGRADED", "UNAVAILABLE", "DISABLED", "UNLICENSED",
        "NOT_INSTALLED", "INCOMPATIBLE", "UPGRADE_REQUIRED",
    }
    if health_ids != expected_health or len(health_rows) != len(expected_health):
        errors.append("health access semantics incomplete")
    health_by_id = {row.get("healthState"): row for row in health_rows}
    if "DIAGNOSTIC" not in health_by_id.get("DEGRADED", {}).get("diagnosticsBehavior", ""):
        errors.append("DEGRADED diagnostics are not governed")
    if "DIAGNOSTIC" not in health_by_id.get("UNAVAILABLE", {}).get("diagnosticsBehavior", ""):
        errors.append("UNAVAILABLE diagnostics are not governed")
    if health_by_id.get("UNLICENSED", {}).get("backendApiBehavior") != "BUSINESS_API_DENIED":
        errors.append("UNLICENSED business API is not denied")
    if health_by_id.get("NOT_INSTALLED", {}).get("backendApiBehavior") != "BUSINESS_API_DENIED":
        errors.append("NOT_INSTALLED business API is not denied")

    lock_rows = enforcement.get("lockPagePolicies", [])
    required_locks = {"UNLICENSED", "NOT_INSTALLED", "DISABLED", "INCOMPATIBLE", "UPGRADE_REQUIRED"}
    if {row.get("lockState") for row in lock_rows} != required_locks:
        errors.append("lock-page states incomplete")
    for row in lock_rows:
        if not set(row.get("allowedMetadataClasses", [])) <= ALLOWED_LOCK_METADATA:
            errors.append(f"{row.get('lockState')}: lock page exposes unapproved metadata")
        if row.get("businessApiAccess") != "DENIED":
            errors.append(f"{row.get('lockState')}: lock page permits business API")

    diagnostic_rows = enforcement.get("diagnosticPolicies", [])
    diagnostic_ids = {row.get("diagnosticClass") for row in diagnostic_rows}
    expected_diagnostics = {
        "PUBLIC_HEALTH_SUMMARY", "AUTHENTICATED_STATUS", "ENGINEER_DIAGNOSTICS",
        "ADMIN_PACKAGE_CONTROL", "INTERNAL_SERVICE_HEALTH",
    }
    if diagnostic_ids != expected_diagnostics:
        errors.append("diagnostic policy classes incomplete")
    for row in diagnostic_rows:
        if set(row.get("requiredPermissions", [])) - permission_ids:
            errors.append(f"{row.get('diagnosticClass')}: unknown diagnostic permission")
        if row.get("diagnosticClass") == "PUBLIC_HEALTH_SUMMARY" and row.get("dataExposure") != "MINIMAL_LIVENESS_OR_READINESS_ONLY":
            errors.append("public diagnostic summary is not minimal")
        if row.get("diagnosticClass") == "ADMIN_PACKAGE_CONTROL":
            if not row.get("controlsAllowed") or row.get("auditPolicy") != "REQUIRED":
                errors.append("admin package controls are not explicitly audited")

    compatibility_rows = enforcement.get("compatibilityPolicies", [])
    compatibility_fields = {
        "currentRoute", "targetRoute", "packageId", "permission", "retirementGate",
        "redirectAllowed", "apiCompatibilityDependency", "rollbackRequirement", "legacyStatus",
    }
    for row in compatibility_rows:
        if set(row) != compatibility_fields:
            errors.append(f"{row.get('currentRoute')}: invalid compatibility mapping")
        if row.get("packageId") not in package_ids:
            errors.append(f"{row.get('currentRoute')}: unknown compatibility package")
        if row.get("permission") not in permission_ids:
            errors.append(f"{row.get('currentRoute')}: unknown compatibility permission")
        if set(row.get("apiCompatibilityDependency", [])) - namespaces:
            errors.append(f"{row.get('currentRoute')}: unknown compatibility namespace")

    review_rows = enforcement.get("reviewQueue", [])
    review_ids = [row.get("reviewId") for row in review_rows]
    known_targets = set(route_ids) | set(menu_ids)
    if len(review_ids) != len(set(review_ids)):
        errors.append("duplicate review ID")
    for row in review_rows:
        if row.get("routeOrMenuId") not in known_targets:
            errors.append(f"{row.get('reviewId')}: unknown review target")
        if row.get("reviewType") not in REVIEW_TYPES:
            errors.append(f"{row.get('reviewId')}: invalid review type")

    if enforcement.get("summary") != enforcement_summary(enforcement):
        errors.append("enforcement summary mismatch")

    serialized = json.dumps({"frontend": front, "enforcement": enforcement}, sort_keys=True)
    if re.search(r"\b20\d{2}-\d{2}-\d{2}\b", serialized) or "/Users/" in serialized:
        errors.append("timestamp or absolute user path found")
    if re.search(r"https?://|localhost|127\.0\.0\.1", serialized, re.IGNORECASE):
        errors.append("live endpoint found")
    if re.search(r"UFMS.{0,40}(endpoint|payload|authentication|pagination|error response)", serialized, re.IGNORECASE):
        errors.append("live UFMS endpoint or implementation detail found")

    completed = subprocess.run(
        [sys.executable, str(BUILDER), "--root", str(ROOT), "--format", "json"],
        capture_output=True, text=True, check=False,
    )
    deterministic = (
        completed.returncode == 0
        and FRONTEND.is_file()
        and FRONTEND.read_text(encoding="utf-8") == completed.stdout
    )
    if not deterministic:
        errors.append("committed frontend inventory differs from deterministic builder output")
    if not isinstance(front.get("unresolvedDeclarations"), list):
        errors.append("unresolved declarations are not represented")

    checks = [
        ("Frontend route inventory", not any("frontend route" in item.lower() or "frontend inventory" in item.lower() for item in errors)),
        ("Menu inventory", not any("menu" in item.lower() or "left navigation" in item.lower() for item in errors)),
        ("Package references", not any("package" in item.lower() and "policy" not in item.lower() for item in errors)),
        ("Permission references", not any("permission" in item.lower() for item in errors)),
        ("Backend namespace policies", not any("backend namespace" in item.lower() for item in errors)),
        ("Package policies", not any("package policy" in item.lower() or "PKG-" in item for item in errors)),
        ("Direct URL policies", not any("direct url" in item.lower() for item in errors)),
        ("Health behavior", not any("health" in item.lower() or "DEGRADED" in item or "UNAVAILABLE" in item for item in errors)),
        ("Lock-page policy", not any("lock page" in item.lower() or "lock-page" in item.lower() for item in errors)),
        ("Diagnostic policy", not any("diagnostic" in item.lower() for item in errors)),
        ("Compatibility mappings", not any("compatibility" in item.lower() for item in errors)),
        ("Runtime honesty", not any("runtime honesty" in item.lower() or "falsely reported" in item.lower() for item in errors)),
        ("Deterministic extraction", deterministic),
    ]
    print("[ONE PACKAGE ROUTE ENFORCEMENT VALIDATION]")
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_PACKAGE_ROUTE_ENFORCEMENT_FAIL")
        return 1
    print("ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
