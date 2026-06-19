#!/usr/bin/env python3
"""Validate the frozen VANTARIS ONE guard contract and route policy registry."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "AN_VANTARIS_ONE/registries/guard-contract.v1.json"
POLICY = ROOT / "AN_VANTARIS_ONE/registries/backend-route-policy.v1.json"
INVENTORY = ROOT / "AN_VANTARIS_ONE/registries/backend-route-inventory.v1.json"
PERMISSIONS = ROOT / "AN_VANTARIS_ONE/registries/permission-registry.v1.json"
PACKAGES = ROOT / "AN_VANTARIS_ONE/registries/package-registry.v1.json"

AUTH_CLASSES = {
    "PUBLIC", "USER_AUTHENTICATED", "SERVICE_AUTHENTICATED",
    "USER_OR_SERVICE_AUTHENTICATED", "INTERNAL_TRUSTED_SERVICE",
    "TEST_ONLY", "DENY_BY_DEFAULT",
}
SCOPE_CLASSES = {
    "GLOBAL_PLATFORM", "TENANT_REQUIRED", "TENANT_OPTIONAL", "SITE_REQUIRED",
    "SITE_OPTIONAL", "RESOURCE_DERIVED", "SERVICE_INTERNAL", "NOT_APPLICABLE",
}
COMPATIBILITY_STAGES = {
    "TARGET_ENFORCED", "LEGACY_AUTH_ONLY", "LEGACY_UNGUARDED",
    "LEGACY_PUBLIC_REVIEW", "TEST_ONLY", "MIGRATION_REQUIRED",
}
IMPLEMENTATION_STATUSES = {
    "ALREADY_COMPLIANT", "AUTHENTICATION_IMPLEMENTATION_REQUIRED",
    "PERMISSION_IMPLEMENTATION_REQUIRED", "SCOPE_IMPLEMENTATION_REQUIRED",
    "PACKAGE_ENFORCEMENT_REQUIRED", "AUDIT_IMPLEMENTATION_REQUIRED",
    "IDEMPOTENCY_IMPLEMENTATION_REQUIRED", "MULTIPLE_CONTROLS_REQUIRED",
    "PUBLIC_REVIEW_REQUIRED", "NON_PRODUCTION", "DEFERRED_COMPATIBILITY",
}
REVIEW_TYPES = {
    "PUBLIC_EXPOSURE", "PERMISSION_GAP", "SCOPE_AMBIGUITY",
    "SERVICE_IDENTITY_POLICY", "LEGACY_COMPATIBILITY",
    "HEALTH_DATA_EXPOSURE", "AUTH_FLOW", "DYNAMIC_BEHAVIOR",
}
ROUTE_FIELDS = {
    "routeId", "sourcePath", "fullPath", "methods", "runtimeClass",
    "owningModule", "packageId", "operationPolicy", "authenticationClass",
    "requiredPermissions", "tenantScopeClass", "siteScopeClass",
    "packageEntitlementRequired", "packageInstalledRequired",
    "packageEnabledRequired", "resourceScopeCheck", "stateTransitionCheck",
    "approvalPolicy", "auditPolicy", "idempotencyPolicy",
    "serviceIdentityAllowed", "publicRouteStatus", "compatibilityStage",
    "implementationStatus", "remediationWorkstream",
    "proposedImplementationTask", "scannerConfidence", "reviewReason", "notes",
}
REVIEW_FIELDS = {
    "routeId", "reviewType", "reason", "currentEvidence",
    "proposedSafeDefault", "owningModule", "requiredDecision",
    "blockingFutureTask", "priority",
}


def load(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name}: {exc}")
        return {}


def deterministic_json(path: Path, value: dict) -> bool:
    return path.read_text(encoding="utf-8") == json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def expected_summary(rows: list[dict], reviews: list[dict]) -> dict:
    auth = Counter(row.get("authenticationClass") for row in rows)
    status = Counter(row.get("implementationStatus") for row in rows)
    modules = Counter(row.get("owningModule") for row in rows)
    packages = Counter(row.get("packageId") or "UNRESOLVED" for row in rows)
    operations = Counter(row.get("operationPolicy") for row in rows)
    return {
        "totalRoutes": len(rows),
        "productionAndLegacyRoutes": sum(row.get("runtimeClass") in {"PRODUCTION", "LEGACY"} for row in rows),
        "testOnlyRoutes": sum(row.get("runtimeClass") == "TEST_ONLY" for row in rows),
        "targetPublicRoutes": auth["PUBLIC"],
        "targetUserAuthenticatedRoutes": auth["USER_AUTHENTICATED"],
        "targetServiceAuthenticatedRoutes": auth["SERVICE_AUTHENTICATED"],
        "targetUserOrServiceRoutes": auth["USER_OR_SERVICE_AUTHENTICATED"],
        "targetInternalServiceRoutes": auth["INTERNAL_TRUSTED_SERVICE"],
        "targetDeniedRoutes": auth["DENY_BY_DEFAULT"],
        "routesWithPermissions": sum(bool(row.get("requiredPermissions")) for row in rows),
        "routesWithoutSuitablePermission": len({
            row.get("routeId") for row in reviews if row.get("reviewType") == "PERMISSION_GAP"
        }),
        "tenantScopedRoutes": sum(row.get("tenantScopeClass") in {"TENANT_REQUIRED", "TENANT_OPTIONAL", "RESOURCE_DERIVED"} for row in rows),
        "siteScopedRoutes": sum(row.get("siteScopeClass") in {"SITE_REQUIRED", "SITE_OPTIONAL", "RESOURCE_DERIVED"} for row in rows),
        "resourceDerivedScopeRoutes": sum("RESOURCE_DERIVED" in {row.get("tenantScopeClass"), row.get("siteScopeClass")} for row in rows),
        "routesRequiringPackageEnforcement": sum(
            bool(row.get("packageEntitlementRequired") or row.get("packageInstalledRequired") or row.get("packageEnabledRequired"))
            for row in rows
        ),
        "routesRequiringAudit": sum(row.get("auditPolicy") == "REQUIRED" for row in rows),
        "routesRequiringIdempotency": sum(row.get("idempotencyPolicy") == "REQUIRED" for row in rows),
        "alreadyCompliantRoutes": status["ALREADY_COMPLIANT"],
        "authenticationImplementationRequired": status["AUTHENTICATION_IMPLEMENTATION_REQUIRED"],
        "permissionImplementationRequired": status["PERMISSION_IMPLEMENTATION_REQUIRED"],
        "packageEnforcementRequired": status["PACKAGE_ENFORCEMENT_REQUIRED"],
        "multipleControlsRequired": status["MULTIPLE_CONTROLS_REQUIRED"],
        "publicReviewRequired": status["PUBLIC_REVIEW_REQUIRED"],
        "reviewQueueCount": len(reviews),
        "routesByOwningModule": dict(sorted(modules.items())),
        "routesByPackage": dict(sorted(packages.items())),
        "routesByOperationPolicy": dict(sorted(operations.items())),
    }


def main() -> int:
    errors: list[str] = []
    for path in (GUARD, POLICY):
        if not path.is_file():
            errors.append(f"missing registry: {path.name}")
    guard = load(GUARD, errors) if GUARD.is_file() else {}
    policy = load(POLICY, errors) if POLICY.is_file() else {}
    inventory = load(INVENTORY, errors)
    permission_registry = load(PERMISSIONS, errors)
    package_registry = load(PACKAGES, errors)

    guard_top = {
        "registryName", "registryVersion", "authority", "status",
        "generatedAtPolicy", "enforcementPrinciples", "authenticationClasses",
        "authorizationStages", "scopeClasses", "operationPolicies",
        "publicRoutePolicy", "serviceIdentityPolicy", "denialResponseCatalog",
        "auditPolicy", "idempotencyPolicy", "compatibilityPolicy",
    }
    policy_top = {
        "registryName", "registryVersion", "authority", "status",
        "generatedAtPolicy", "sourceInventory", "summary",
        "routePolicies", "reviewQueue",
    }
    if set(guard) != guard_top:
        errors.append("guard contract has invalid top-level fields")
    if set(policy) != policy_top:
        errors.append("route policy registry has invalid top-level fields")
    fixed_guard = {
        "registryName": "VANTARIS ONE Guard Contract",
        "registryVersion": "1.0.0",
        "authority": "ONE-A5-P0-05",
        "status": "FROZEN_FOR_GUARD_IMPLEMENTATION",
        "generatedAtPolicy": "STATIC_ARCHITECTURE_BASELINE",
    }
    fixed_policy = {
        "registryName": "VANTARIS ONE Backend Route Policy Registry",
        "registryVersion": "1.0.0",
        "authority": "ONE-A5-P0-05",
        "status": "FROZEN_ROUTE_POLICY_BASELINE",
        "generatedAtPolicy": "STATIC_ARCHITECTURE_BASELINE",
        "sourceInventory": "backend-route-inventory.v1.json",
    }
    for field, value in fixed_guard.items():
        if guard.get(field) != value:
            errors.append(f"guard contract invalid {field}")
    for field, value in fixed_policy.items():
        if policy.get(field) != value:
            errors.append(f"route policy invalid {field}")

    auth_rows = guard.get("authenticationClasses", [])
    auth_ids = {row.get("classId") for row in auth_rows}
    if auth_ids != AUTH_CLASSES or len(auth_rows) != len(AUTH_CLASSES):
        errors.append("authentication classes are incomplete or duplicated")
    auth_fields = {
        "classId", "acceptedCredentialTypes", "tokenOrSessionRequirement",
        "tenantClaimRequirement", "siteClaimBehavior", "serviceIdentitySupport",
        "auditBehavior", "failureResponse", "permittedRuntimeClasses",
    }
    if any(set(row) != auth_fields for row in auth_rows):
        errors.append("authentication class structure invalid")

    stages = guard.get("authorizationStages", [])
    expected_stage_order = [
        "AUTHENTICATION", "IDENTITY_STATUS", "TENANT_MEMBERSHIP", "SITE_SCOPE",
        "PACKAGE_ENTITLEMENT", "PACKAGE_INSTALLED", "PACKAGE_ENABLED",
        "PERMISSION", "RESOURCE_OWNERSHIP_OBJECT_SCOPE", "STATE_TRANSITION_RULE",
        "ACTION_APPROVAL", "AUDIT_RECORD",
    ]
    if [row.get("stageId") for row in stages] != expected_stage_order:
        errors.append("authorization stage order invalid")
    stage_fields = {
        "stageId", "purpose", "authoritativeProvider", "input", "decision",
        "denialCode", "auditRequirement", "failurePolicy",
    }
    if any(set(row) != stage_fields for row in stages):
        errors.append("authorization stage structure invalid")
    if any(not str(row.get("failurePolicy", "")).startswith("FAIL_CLOSED") for row in stages):
        errors.append("authorization stages must fail closed")

    scope_rows = guard.get("scopeClasses", [])
    scope_ids = {row.get("scopeClassId") for row in scope_rows}
    if scope_ids != SCOPE_CLASSES or len(scope_rows) != len(SCOPE_CLASSES):
        errors.append("scope classes are incomplete or duplicated")
    scope_fields = {
        "scopeClassId", "requiredClaims", "resourceLookupBehavior",
        "crossTenantProhibition", "crossSiteProhibition",
        "administratorBehavior", "serviceIdentityBehavior", "auditRequirement",
    }
    if any(set(row) != scope_fields for row in scope_rows):
        errors.append("scope class structure invalid")
    if any("NO_AUTOMATIC_BYPASS" not in row.get("administratorBehavior", "") for row in scope_rows):
        errors.append("administrator isolation policy missing")

    operations = guard.get("operationPolicies", [])
    operation_ids = {row.get("policyId") for row in operations}
    expected_operations = {
        "READ_PUBLIC", "READ_PROTECTED", "READ_SENSITIVE", "CREATE", "UPDATE",
        "DELETE", "INTAKE", "CONTROL", "EXPORT", "STREAM", "AUTHENTICATION",
        "HEALTH_PUBLIC", "HEALTH_PROTECTED", "TEST_ONLY",
    }
    if operation_ids != expected_operations or len(operations) != len(expected_operations):
        errors.append("operation policies are incomplete or duplicated")
    operation_fields = {
        "policyId", "authenticationClass", "permissionRequired", "scopeRequirement",
        "packageEnforcementRequired", "auditRequired", "idempotencyRequired",
        "approvalMayBeRequired", "serviceIdentityAllowed", "compatibilityMode",
        "defaultDenialCode",
    }
    if any(set(row) != operation_fields for row in operations):
        errors.append("operation policy structure invalid")

    required_denials = {
        "AUTHENTICATION_REQUIRED", "INVALID_CREDENTIAL", "IDENTITY_DISABLED",
        "TENANT_MEMBERSHIP_REQUIRED", "SITE_SCOPE_REQUIRED", "TENANT_SCOPE_DENIED",
        "SITE_SCOPE_DENIED", "ENTITLEMENT_REQUIRED", "PACKAGE_NOT_INSTALLED",
        "PACKAGE_DISABLED", "PACKAGE_INCOMPATIBLE", "PERMISSION_DENIED",
        "RESOURCE_SCOPE_DENIED", "ACTION_NOT_ALLOWED", "APPROVAL_REQUIRED",
        "IDEMPOTENCY_KEY_REQUIRED", "SERVICE_IDENTITY_DENIED",
        "PUBLIC_ROUTE_NOT_ALLOWED", "POLICY_UNAVAILABLE",
    }
    denial_rows = guard.get("denialResponseCatalog", [])
    denial_ids = {row.get("code") for row in denial_rows}
    if denial_ids != required_denials or len(denial_rows) != len(required_denials):
        errors.append("denial response catalog incomplete or duplicated")
    denial_fields = {
        "code", "httpStatusRecommendation", "publicMessage", "auditSeverity",
        "retryable", "detailsExposurePolicy",
    }
    if any(set(row) != denial_fields for row in denial_rows):
        errors.append("denial response structure invalid")

    inventory_rows = inventory.get("routes", [])
    inventory_by_id = {row.get("routeId"): row for row in inventory_rows}
    rows = policy.get("routePolicies", [])
    row_ids = [row.get("routeId") for row in rows]
    if len(row_ids) != len(set(row_ids)):
        errors.append("duplicate route policy routeId")
    if set(row_ids) != set(inventory_by_id):
        errors.append("route policy coverage differs from source inventory")
    if len(rows) != 181:
        errors.append("route policy registry must contain all 181 routes")
    if row_ids != sorted(row_ids):
        errors.append("route policies must be deterministically sorted by routeId")

    permission_names = {row.get("permission") for row in permission_registry.get("permissions", [])}
    package_by_id = {row.get("packageId"): row for row in package_registry.get("packages", [])}
    public_routes = guard.get("publicRoutePolicy", {}).get("routes", [])
    public_ids = [row.get("routeId") for row in public_routes]
    if len(public_ids) != len(set(public_ids)):
        errors.append("duplicate public route policy")
    public_fields = {
        "routeId", "rationale", "exposedDataClass", "rateLimitRequired",
        "sensitiveFieldPolicy", "auditPolicy", "reviewStatus", "category",
    }
    if any(set(row) != public_fields for row in public_routes):
        errors.append("public route policy structure invalid")

    review_rows = policy.get("reviewQueue", [])
    if review_rows != sorted(review_rows, key=lambda row: (row.get("routeId"), row.get("reviewType"))):
        errors.append("review queue must be deterministically sorted")
    for review in review_rows:
        if set(review) != REVIEW_FIELDS:
            errors.append(f"{review.get('routeId')}: invalid review structure")
        if review.get("routeId") not in inventory_by_id:
            errors.append(f"{review.get('routeId')}: unknown review routeId")
        if review.get("reviewType") not in REVIEW_TYPES:
            errors.append(f"{review.get('routeId')}: invalid review type")

    permission_gap_ids = {row.get("routeId") for row in review_rows if row.get("reviewType") == "PERMISSION_GAP"}
    health_review_ids = {row.get("routeId") for row in review_rows if row.get("reviewType") == "HEALTH_DATA_EXPOSURE"}
    for row in rows:
        rid = row.get("routeId")
        source = inventory_by_id.get(rid, {})
        if set(row) != ROUTE_FIELDS:
            errors.append(f"{rid}: invalid route policy structure")
        if row.get("sourcePath") != source.get("sourcePath"):
            errors.append(f"{rid}: sourcePath differs from inventory")
        if row.get("fullPath") != source.get("fullPath"):
            errors.append(f"{rid}: fullPath differs from inventory")
        if row.get("methods") != source.get("methods"):
            errors.append(f"{rid}: methods differ from inventory")
        if row.get("runtimeClass") != source.get("runtimeClass"):
            errors.append(f"{rid}: runtimeClass differs from inventory")
        if row.get("authenticationClass") not in AUTH_CLASSES:
            errors.append(f"{rid}: invalid authentication class")
        if row.get("operationPolicy") not in operation_ids:
            errors.append(f"{rid}: unknown operation policy")
        if row.get("tenantScopeClass") not in SCOPE_CLASSES or row.get("siteScopeClass") not in SCOPE_CLASSES:
            errors.append(f"{rid}: invalid scope class")
        unknown_permissions = set(row.get("requiredPermissions", [])) - permission_names
        if unknown_permissions:
            errors.append(f"{rid}: unknown permission reference")
        if row.get("packageId") and row.get("packageId") not in package_by_id:
            errors.append(f"{rid}: unknown packageId")
        if row.get("compatibilityStage") not in COMPATIBILITY_STAGES:
            errors.append(f"{rid}: invalid compatibility stage")
        if row.get("implementationStatus") not in IMPLEMENTATION_STATUSES:
            errors.append(f"{rid}: invalid implementation status")
        if row.get("authenticationClass") == "PUBLIC":
            if rid not in public_ids or row.get("publicRouteStatus") != "ALLOWLISTED":
                errors.append(f"{rid}: public route missing explicit allowlist")
        elif rid in public_ids:
            errors.append(f"{rid}: public allowlist conflicts with target authentication")
        if source.get("runtimeClass") == "TEST_ONLY":
            if row.get("authenticationClass") != "TEST_ONLY" or row.get("implementationStatus") != "NON_PRODUCTION":
                errors.append(f"{rid}: test route is not explicitly non-production")
        elif row.get("authenticationClass") in {"TEST_ONLY"}:
            errors.append(f"{rid}: production/legacy route classified test-only")
        if source.get("runtimeClass") != "TEST_ONLY" and row.get("authenticationClass") not in AUTH_CLASSES - {"TEST_ONLY"}:
            errors.append(f"{rid}: production target authentication unclassified")
        if source.get("permissionClass") == "AUTH_ONLY" and row.get("authenticationClass") not in {"PUBLIC", "TEST_ONLY"}:
            if not row.get("requiredPermissions") and rid not in permission_gap_ids:
                errors.append(f"{rid}: AUTH_ONLY route lacks target permission or explicit permission gap")
        if source.get("permissionClass") == "UNGUARDED" and source.get("runtimeClass") != "TEST_ONLY":
            if row.get("authenticationClass") == "PUBLIC" and source.get("authenticationClass") != "EXPLICITLY_PUBLIC":
                errors.append(f"{rid}: unguarded route silently classified public")
        op = row.get("operationPolicy")
        if op in {"READ_SENSITIVE", "CREATE", "UPDATE", "DELETE", "INTAKE", "CONTROL", "EXPORT", "STREAM", "AUTHENTICATION"}:
            if row.get("auditPolicy") != "REQUIRED":
                errors.append(f"{rid}: sensitive/mutation route lacks audit policy")
        if op in {"INTAKE", "CONTROL"} and row.get("idempotencyPolicy") != "REQUIRED":
            errors.append(f"{rid}: intake/control route lacks idempotency policy")
        package = package_by_id.get(row.get("packageId"))
        if package and not package.get("mandatory") and source.get("runtimeClass") != "TEST_ONLY":
            if row.get("authenticationClass") != "PUBLIC":
                if not all(row.get(field) is True for field in (
                    "packageEntitlementRequired", "packageInstalledRequired", "packageEnabledRequired"
                )):
                    errors.append(f"{rid}: optional-package business route lacks full package enforcement")
        if op == "HEALTH_PROTECTED" and rid not in health_review_ids:
            errors.append(f"{rid}: protected health route lacks exposure review")
        if row.get("implementationStatus") == "ALREADY_COMPLIANT" and row.get("authenticationClass") not in {"PUBLIC", "TEST_ONLY"}:
            if "Missing controls: NONE" not in row.get("notes", []):
                errors.append(f"{rid}: current runtime enforcement is misrepresented")
        if not any("Target policy only" in note for note in row.get("notes", [])):
            errors.append(f"{rid}: runtime honesty note missing")

    if set(public_ids) != {row.get("routeId") for row in rows if row.get("authenticationClass") == "PUBLIC"}:
        errors.append("public route policy does not reconcile with route policies")
    if policy.get("summary") != expected_summary(rows, review_rows):
        errors.append("summary counts do not reconcile")

    serialized = json.dumps({"guard": guard, "policy": policy}, sort_keys=True)
    if re.search(r"\b20\d{2}-\d{2}-\d{2}\b", serialized) or "/Users/" in serialized:
        errors.append("timestamp or absolute user path found")
    if re.search(r"https?://|localhost|127\.0\.0\.1", serialized, re.IGNORECASE):
        errors.append("live endpoint found")
    if re.search(r"UFMS.{0,30}(endpoint|payload|authentication|pagination|error response)", serialized, re.IGNORECASE):
        errors.append("live UFMS implementation detail found")
    if GUARD.is_file() and guard and not deterministic_json(GUARD, guard):
        errors.append("guard contract JSON serialization is not deterministic")
    if POLICY.is_file() and policy and not deterministic_json(POLICY, policy):
        errors.append("route policy JSON serialization is not deterministic")

    categories = {
        "Guard contract structure": (
            "guard contract" not in " ".join(errors)
            and not any(term in item for item in errors for term in (
                "authentication classes", "authorization stage", "scope classes",
                "operation policies", "denial response"
            ))
        ),
        "Route policy coverage": not any(term in item for item in errors for term in (
            "coverage", "181 routes", "duplicate route policy", "unknown review routeId",
            "differs from inventory", "invalid route policy structure",
        )),
        "Authentication policy": not any("authentication" in item.lower() or "public route" in item.lower() or "silently classified public" in item.lower() for item in errors),
        "Permission references": not any("permission" in item.lower() for item in errors),
        "Scope policy": not any("scope" in item.lower() for item in errors),
        "Package enforcement policy": not any("package" in item.lower() for item in errors),
        "Audit policy": not any("audit" in item.lower() for item in errors),
        "Idempotency policy": not any("idempotency" in item.lower() for item in errors),
        "Public route policy": not any("public" in item.lower() for item in errors),
        "Review queue": not any("review" in item.lower() for item in errors),
        "Runtime honesty": not any("runtime" in item.lower() or "misrepresented" in item.lower() for item in errors),
    }
    print("[ONE GUARD CONTRACT VALIDATION]")
    for label, passed in categories.items():
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        print("ONE_GUARD_CONTRACT_FAIL")
        return 1
    print("ONE_GUARD_CONTRACT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
