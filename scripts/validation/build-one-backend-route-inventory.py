#!/usr/bin/env python3
"""Build the deterministic VANTARIS ONE backend HTTP route inventory."""
from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

INVENTORY_PATH = "AN_VANTARIS_ONE/registries/backend-route-inventory.v1.json"
SOURCE_ROOT = "AN_VANTARIS_IBMS-backend/src"
AUTH_DECORATORS = {"jwt_required", "login_required", "auth_required", "token_required"}
PERMISSION_DECORATORS = {"require_permission", "require_any_permission", "permission_required", "authorize", "policy_required"}
PUBLIC_ROUTES = {("/api/did/login", "POST"), ("/api/did/challenge", "GET")}
TEST_PATH_PARTS = {"tests", "testMQTT"}
CONTROL_WORDS = {"replay", "enable", "disable", "approve", "dispatch", "close", "escalate", "configure", "command", "reconnect", "switch", "revoke", "reissue", "train"}
INTAKE_WORDS = {"ingest", "intake", "register", "upload"}
EXPORT_WORDS = {"export", "download"}
HEALTH_WORDS = {"health", "ready", "readiness"}
STREAM_WORDS = {"stream", "sse", "subscribe"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--format", choices=("json",), default="json")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def decorator_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return decorator_name(node.func)
    return ""


def strings(node: ast.AST) -> List[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        values: List[str] = []
        for item in node.elts:
            values.extend(strings(item))
        return values
    return []


def literal_string(node: ast.AST) -> Optional[str]:
    values = strings(node)
    return values[0] if len(values) == 1 else None


def source_candidates(source_root: Path) -> Iterable[Path]:
    for path in sorted(source_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if "tests" in path.parts:
            continue
        name = path.name.lower()
        relative = path.relative_to(source_root).as_posix().lower()
        if (
            relative.startswith("api/")
            or name == "main.py"
            or "controller" in name
            or "route" in name
            or name.startswith("api")
            or "testmqtt/" in relative
        ):
            yield path


def discover_blueprints(source_root: Path) -> Tuple[Dict[str, Dict[str, str]], List[Dict[str, Any]]]:
    blueprints: Dict[str, Dict[str, str]] = {}
    unresolved: List[Dict[str, Any]] = []
    for path in source_candidates(source_root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            if not isinstance(value, ast.Call) or decorator_name(value.func) != "Blueprint":
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            variable = next((target.id for target in targets if isinstance(target, ast.Name)), None)
            if not variable:
                continue
            blueprint_name = literal_string(value.args[0]) if value.args else None
            prefix = ""
            prefix_resolved = True
            for keyword in value.keywords:
                if keyword.arg == "url_prefix":
                    literal = literal_string(keyword.value)
                    if literal is None:
                        prefix_resolved = False
                    else:
                        prefix = literal
            if blueprint_name is None or not prefix_resolved:
                unresolved.append({
                    "sourcePath": path.relative_to(source_root.parent.parent).as_posix(),
                    "line": getattr(node, "lineno", None),
                    "symbol": variable,
                    "unresolvedType": "DYNAMIC_BLUEPRINT_DECLARATION",
                    "evidence": ast.get_source_segment(path.read_text(encoding="utf-8"), node) or variable,
                    "requiredReview": "Resolve Blueprint name or url_prefix statically.",
                    "scannerConfidence": "HIGH",
                })
            else:
                blueprints[variable] = {"blueprintName": blueprint_name, "blueprintPrefix": prefix}
    return blueprints, unresolved


def discover_registrations(source_root: Path, blueprints: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
    unresolved: List[Dict[str, Any]] = []
    for path in source_candidates(source_root):
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or decorator_name(node.func) != "register_blueprint":
                continue
            symbol = node.args[0].id if node.args and isinstance(node.args[0], ast.Name) else ""
            if symbol in blueprints:
                continue
            unresolved.append({
                "sourcePath": path.relative_to(source_root.parent.parent).as_posix(),
                "line": getattr(node, "lineno", None),
                "symbol": symbol or "register_blueprint",
                "unresolvedType": "UNRESOLVED_BLUEPRINT_REGISTRATION",
                "evidence": ast.get_source_segment(text, node) or "register_blueprint(...)",
                "requiredReview": "Resolve imported Blueprint and effective prefix.",
                "scannerConfidence": "MEDIUM",
            })
    return unresolved


def path_match(path: str, pattern: str) -> bool:
    if "*" in pattern:
        return fnmatch.fnmatch(path, pattern)
    return path == pattern or path.startswith(pattern.rstrip("/") + "/")


def namespace_mapping(full_path: str, api_rows: List[Dict[str, Any]]) -> Tuple[str, Optional[Dict[str, Any]], str]:
    matches: List[Tuple[int, int, int, str, Dict[str, Any], str]] = []
    for row in api_rows:
        namespace = row["namespace"]
        if full_path == namespace or full_path.startswith(namespace + "/"):
            matches.append((len([part for part in namespace.split("/") if part]), len(namespace), 1, "TARGET_NAMESPACE", row, namespace))
    for row in api_rows:
        for legacy in row.get("legacyMappings", []):
            if path_match(full_path, legacy):
                matches.append((len([part for part in legacy.split("/") if part]), len(legacy.replace("*", "")), 0, "LEGACY_COMPATIBILITY", row, legacy))
    if matches:
        matches.sort(key=lambda item: (-item[0], -item[1], -item[2], item[4]["namespace"]))
        _, _, _, status, row, matched = matches[0]
        return status, row, matched
    return "UNRESOLVED", None, current_namespace(full_path)


def current_namespace(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
        return "/" + "/".join(parts[:3])
    if len(parts) >= 2:
        return "/" + "/".join(parts[:2])
    return path


def method_operation(method: str, path: str, symbol: str) -> str:
    lower = f"{path} {symbol}".lower()
    if any(word in lower for word in HEALTH_WORDS):
        return "HEALTH"
    if any(word in lower for word in STREAM_WORDS):
        return "STREAM"
    if any(word in lower for word in EXPORT_WORDS):
        return "EXPORT"
    if any(word in lower for word in CONTROL_WORDS):
        return "CONTROL"
    if any(word in lower for word in INTAKE_WORDS) and method == "POST":
        return "INTAKE"
    if "login" in lower or "challenge" in lower:
        return "AUTH"
    if method in {"GET", "HEAD", "OPTIONS"}:
        return "READ"
    if method in {"POST", "PUT", "PATCH", "DELETE"}:
        return "WRITE"
    return "UNKNOWN"


def operation_class(methods: Sequence[str], path: str, symbol: str) -> str:
    classes = {method_operation(method, path, symbol) for method in methods}
    return next(iter(classes)) if len(classes) == 1 else "MIXED"


def route_id(methods: Sequence[str], full_path: str, symbol: str) -> str:
    method_token = "-".join(methods)
    stable = hashlib.sha256(f"{method_token}|{full_path}|{symbol}".encode("utf-8")).hexdigest()[:12].upper()
    return f"ROUTE-{method_token}-{stable}"


def scope_classes(api_row: Optional[Dict[str, Any]], runtime_class: str) -> Tuple[str, str]:
    if runtime_class == "TEST_ONLY":
        return "NOT_APPLICABLE", "NOT_APPLICABLE"
    if not api_row:
        return "UNDECLARED", "UNDECLARED"
    if not api_row.get("tenantScoped"):
        tenant = "GLOBAL_PLATFORM"
    else:
        tenant = "TENANT_REQUIRED"
    if not api_row.get("siteScoped"):
        site = "TENANT_LEVEL" if api_row.get("tenantScoped") else "GLOBAL_PLATFORM"
    else:
        site = "SITE_REQUIRED"
    return tenant, site


def proposed_remediation(auth_class: str, permission_class: str, package_class: str, namespace_status: str, audit_class: str, idem_class: str) -> Tuple[str, str]:
    if auth_class == "UNCLASSIFIED":
        return "WS-P0-SECURITY-GUARDS", "ONE-A5-P0-04"
    if permission_class in {"AUTH_ONLY", "UNGUARDED"}:
        return "WS-P0-SECURITY-GUARDS", "ONE-A5-P0-05"
    if package_class in {"NOT_DECLARED", "INFERRED_ONLY"}:
        return "WS-P0-PACKAGE-ENFORCEMENT", "ONE-A5-P0-06"
    if audit_class == "REQUIRED_NOT_DECLARED" or idem_class == "REQUIRED_NOT_DECLARED":
        return "WS-P0-AUDIT-IDEMPOTENCY", "ONE-A5-P0-07"
    if namespace_status != "TARGET_NAMESPACE":
        return "WS-P1-API-NAMESPACE", "ONE-A5-P1-02"
    return "NOT_APPLICABLE", "NOT_APPLICABLE"


def extract_routes(root: Path) -> Dict[str, Any]:
    source_root = root / SOURCE_ROOT
    api_registry = load_json(root / "AN_VANTARIS_ONE/registries/api-namespace-registry.v1.json")
    package_registry = load_json(root / "AN_VANTARIS_ONE/registries/package-registry.v1.json")
    permission_registry = load_json(root / "AN_VANTARIS_ONE/registries/permission-registry.v1.json")
    api_rows = api_registry["apiNamespaces"]
    package_ids = {row["packageId"] for row in package_registry["packages"]}
    known_permissions = {row["permission"] for row in permission_registry["permissions"]}
    blueprints, unresolved = discover_blueprints(source_root)
    unresolved.extend(discover_registrations(source_root, blueprints))
    routes: List[Dict[str, Any]] = []

    for path in source_candidates(source_root):
        relative = rel(root, path)
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            decorators = []
            route_decorators = []
            raw_permissions: List[str] = []
            for dec in node.decorator_list:
                name = decorator_name(dec)
                decorators.append(name)
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == "route":
                    variable = dec.func.value.id if isinstance(dec.func.value, ast.Name) else ""
                    route_path = literal_string(dec.args[0]) if dec.args else None
                    methods = ["GET"]
                    for keyword in dec.keywords:
                        if keyword.arg == "methods":
                            methods = strings(keyword.value) or methods
                    if route_path is None:
                        unresolved.append({
                            "sourcePath": relative,
                            "line": getattr(dec, "lineno", None),
                            "symbol": node.name,
                            "unresolvedType": "DYNAMIC_ROUTE_PATH",
                            "evidence": ast.get_source_segment(text, dec) or "@route(...)",
                            "requiredReview": "Resolve dynamic route path.",
                            "scannerConfidence": "HIGH",
                        })
                    else:
                        route_decorators.append((variable, route_path, sorted(set(method.upper() for method in methods)), getattr(dec, "lineno", node.lineno)))
                if isinstance(dec, ast.Call) and name in PERMISSION_DECORATORS:
                    for arg in dec.args:
                        raw_permissions.extend(strings(arg))
            if not route_decorators:
                continue
            body_source = ast.get_source_segment(text, node) or ""
            for variable, route_path, methods, line in route_decorators:
                blueprint = blueprints.get(variable)
                prefix = blueprint["blueprintPrefix"] if blueprint else ""
                blueprint_name = blueprint["blueprintName"] if blueprint else variable
                full_path = (prefix.rstrip("/") + "/" + route_path.lstrip("/")) if prefix else route_path
                if not full_path.startswith("/"):
                    full_path = "/" + full_path
                runtime_class = "TEST_ONLY" if any(part in TEST_PATH_PARTS for part in path.parts) else ("LEGACY" if not full_path.startswith("/api/v1/") else "PRODUCTION")
                namespace_status, api_row, current_match = namespace_mapping(full_path, api_rows)
                target_namespace = api_row["namespace"] if api_row else ""
                package_id = api_row["packageId"] if api_row and api_row["packageId"] in package_ids else ""
                owning_module = api_row["owningModule"] if api_row else "UNRESOLVED"
                operation = operation_class(methods, full_path, node.name)
                explicit_public = all((full_path, method) in PUBLIC_ROUTES for method in methods)
                authenticated = any(name in AUTH_DECORATORS for name in decorators)
                permission_guarded = any(name in PERMISSION_DECORATORS for name in decorators)
                resolved_permissions = sorted({permission for permission in raw_permissions if permission in known_permissions})
                legacy_permissions = sorted({permission for permission in raw_permissions if permission not in known_permissions})
                if runtime_class == "TEST_ONLY":
                    auth_class = "UNCLASSIFIED"
                elif explicit_public:
                    auth_class = "EXPLICITLY_PUBLIC"
                elif authenticated:
                    auth_class = "AUTHENTICATED"
                else:
                    auth_class = "UNCLASSIFIED"
                if explicit_public:
                    permission_class = "NOT_APPLICABLE"
                elif permission_guarded:
                    permission_class = "PERMISSION_GUARDED"
                elif authenticated:
                    permission_class = "AUTH_ONLY"
                else:
                    permission_class = "UNGUARDED"
                tenant_scope, site_scope = scope_classes(api_row, runtime_class)
                if runtime_class == "TEST_ONLY":
                    package_enforcement = "NOT_APPLICABLE"
                elif package_id:
                    package_enforcement = "INFERRED_ONLY"
                else:
                    package_enforcement = "NOT_DECLARED"
                requires_audit = operation in {"WRITE", "CONTROL", "INTAKE", "EXPORT", "MIXED"}
                audit_declared = any(token in body_source.lower() for token in ("log_sensitive_api", "auditrecord", "audit_record", "audit_event"))
                audit_class = "REQUIRED_DECLARED" if requires_audit and audit_declared else ("REQUIRED_NOT_DECLARED" if requires_audit else "NOT_APPLICABLE")
                requires_idempotency = any(method == "POST" for method in methods) and operation in {"WRITE", "CONTROL", "INTAKE", "EXPORT", "MIXED"}
                idempotency_declared = "idempotency" in body_source.lower() or "idempotency-key" in body_source.lower()
                idem_class = "REQUIRED_DECLARED" if requires_idempotency and idempotency_declared else ("REQUIRED_NOT_DECLARED" if requires_idempotency else "NOT_REQUIRED")
                if explicit_public:
                    exposure = "PUBLIC_SAFE" if operation == "AUTH" else "PUBLIC_SENSITIVE"
                elif auth_class == "AUTHENTICATED":
                    exposure = "PROTECTED"
                else:
                    exposure = "UNCLASSIFIED"
                if runtime_class == "TEST_ONLY":
                    legacy_status = "REVIEW_REQUIRED"
                elif namespace_status == "TARGET_NAMESPACE":
                    legacy_status = "CURRENT_TARGET"
                elif namespace_status == "LEGACY_COMPATIBILITY":
                    legacy_status = "LEGACY_COMPATIBILITY_REQUIRED"
                elif full_path.startswith("/api/"):
                    legacy_status = "LEGACY_MIGRATE"
                else:
                    legacy_status = "REVIEW_REQUIRED"
                workstream, task = proposed_remediation(auth_class, permission_class, package_enforcement, namespace_status, audit_class, idem_class)
                notes = []
                if legacy_permissions:
                    notes.append("Legacy permission codes not present in frozen permission registry: " + ", ".join(legacy_permissions))
                if runtime_class == "TEST_ONLY":
                    notes.append("Standalone test/simulator route; not registered on the main API blueprint.")
                if namespace_status == "UNRESOLVED":
                    notes.append("Target namespace requires manual ownership mapping.")
                routes.append({
                    "routeId": route_id(methods, full_path, node.name),
                    "sourcePath": relative,
                    "line": line,
                    "symbol": node.name,
                    "blueprintName": blueprint_name,
                    "blueprintPrefix": prefix,
                    "routePath": route_path,
                    "fullPath": full_path,
                    "methods": methods,
                    "runtimeClass": runtime_class,
                    "owningModule": owning_module,
                    "packageId": package_id,
                    "currentNamespace": current_namespace(full_path),
                    "targetNamespace": target_namespace,
                    "namespaceStatus": namespace_status if namespace_status != "UNRESOLVED" else ("NAMESPACE_DRIFT" if full_path.startswith("/api/") else "UNRESOLVED"),
                    "operationClass": operation,
                    "authenticationClass": auth_class,
                    "authenticationEvidence": sorted({name for name in decorators if name in AUTH_DECORATORS}) or (["STATIC_PUBLIC_ALLOWLIST"] if explicit_public else []),
                    "permissionClass": permission_class,
                    "declaredPermissions": resolved_permissions,
                    "permissionEvidence": sorted({name for name in decorators if name in PERMISSION_DECORATORS}) + legacy_permissions,
                    "tenantScopeClass": tenant_scope,
                    "siteScopeClass": site_scope,
                    "packageEnforcementClass": package_enforcement,
                    "auditClass": audit_class,
                    "idempotencyClass": idem_class,
                    "publicExposureClass": exposure,
                    "legacyStatus": legacy_status,
                    "compatibilityRequirement": "PRESERVE_UNTIL_TARGET_PARITY" if legacy_status in {"LEGACY_COMPATIBILITY_REQUIRED", "LEGACY_MIGRATE"} else "NOT_APPLICABLE",
                    "remediationWorkstream": workstream,
                    "proposedTaskId": task,
                    "scannerConfidence": "HIGH" if blueprint or runtime_class == "TEST_ONLY" else "MEDIUM",
                    "notes": notes,
                })

    routes.sort(key=lambda row: (row["fullPath"], row["methods"], row["sourcePath"], row["line"] or 0, row["symbol"]))
    unresolved.sort(key=lambda row: (row["sourcePath"], row["line"] or 0, row["symbol"], row["unresolvedType"]))
    counts = Counter()
    routes_by_module = Counter()
    routes_by_package = Counter()
    routes_by_namespace = Counter()
    for route in routes:
        counts["totalRoutes"] += 1
        counts[{"PRODUCTION": "productionRoutes", "LEGACY": "legacyRoutes", "TEST_ONLY": "testOnlyRoutes", "UNKNOWN": "unresolvedRoutes"}[route["runtimeClass"]]] += 1
        counts[{"AUTHENTICATED": "authenticatedRoutes", "EXPLICITLY_PUBLIC": "explicitlyPublicRoutes", "UNCLASSIFIED": "unclassifiedAuthRoutes", "INHERITED_UNKNOWN": "unclassifiedAuthRoutes"}[route["authenticationClass"]]] += 1
        if route["permissionClass"] in {"ACTION_GUARDED", "PERMISSION_GUARDED"}:
            counts["permissionGuardedRoutes"] += 1
        elif route["permissionClass"] == "AUTH_ONLY":
            counts["authOnlyRoutes"] += 1
        elif route["permissionClass"] == "UNGUARDED":
            counts["unguardedRoutes"] += 1
        if route["operationClass"] in {"WRITE", "CONTROL", "INTAKE", "EXPORT", "MIXED"}:
            counts["mutationRoutes"] += 1
            if route["permissionClass"] not in {"ACTION_GUARDED", "PERMISSION_GUARDED"}:
                counts["mutationWithoutActionGuard"] += 1
        if route["auditClass"] == "REQUIRED_NOT_DECLARED":
            counts["auditRequiredNotDeclared"] += 1
        if route["idempotencyClass"] == "REQUIRED_NOT_DECLARED":
            counts["idempotencyRequiredNotDeclared"] += 1
        counts[{"DECLARED": "packageDeclaredRoutes", "INFERRED_ONLY": "packageInferredRoutes", "NOT_DECLARED": "packageNotDeclaredRoutes", "NOT_APPLICABLE": "packageNotDeclaredRoutes", "UNRESOLVED": "packageNotDeclaredRoutes"}[route["packageEnforcementClass"]]] += 1
        counts[{"TARGET_NAMESPACE": "targetNamespaceRoutes", "LEGACY_COMPATIBILITY": "legacyCompatibilityRoutes", "NAMESPACE_DRIFT": "namespaceDriftRoutes", "UNRESOLVED": "namespaceDriftRoutes"}[route["namespaceStatus"]]] += 1
        routes_by_module[route["owningModule"]] += 1
        routes_by_package[route["packageId"] or "UNRESOLVED"] += 1
        routes_by_namespace[route["currentNamespace"]] += 1
    counts["unresolvedRoutes"] = len(unresolved)
    summary = {key: counts[key] for key in (
        "totalRoutes", "productionRoutes", "legacyRoutes", "testOnlyRoutes", "unresolvedRoutes",
        "authenticatedRoutes", "explicitlyPublicRoutes", "unclassifiedAuthRoutes",
        "permissionGuardedRoutes", "authOnlyRoutes", "unguardedRoutes", "mutationRoutes",
        "mutationWithoutActionGuard", "auditRequiredNotDeclared", "idempotencyRequiredNotDeclared",
        "packageDeclaredRoutes", "packageInferredRoutes", "packageNotDeclaredRoutes",
        "targetNamespaceRoutes", "legacyCompatibilityRoutes", "namespaceDriftRoutes",
    )}
    summary["routesByModule"] = dict(sorted(routes_by_module.items()))
    summary["routesByPackage"] = dict(sorted(routes_by_package.items()))
    summary["routesByCurrentNamespace"] = dict(sorted(routes_by_namespace.items()))
    return {
        "registryName": "VANTARIS ONE Backend Route Inventory",
        "registryVersion": "1.0.0",
        "authority": "ONE-A5-P0-04",
        "status": "FROZEN_ROUTE_CLASSIFICATION_BASELINE",
        "generatedAtPolicy": "STATIC_ARCHITECTURE_BASELINE",
        "sourceRoot": SOURCE_ROOT,
        "extractionPolicy": {
            "mode": "STATIC_AST_ONLY",
            "backendImportExecution": False,
            "databaseConnection": False,
            "testRoutesSeparated": True,
            "packageRegistryMembershipIsEnforcement": False,
        },
        "summary": summary,
        "routes": routes,
        "unresolvedRegistrations": unresolved,
    }


def render(document: Dict[str, Any]) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    document = extract_routes(root)
    rendered = render(document)
    committed = root / INVENTORY_PATH
    if args.check:
        if not committed.is_file():
            print(f"FAIL: committed inventory missing: {INVENTORY_PATH}")
            return 1
        if committed.read_text(encoding="utf-8") != rendered:
            print("FAIL: committed backend route inventory differs from deterministic extraction")
            return 1
        print("PASS: committed backend route inventory matches deterministic extraction")
        return 0
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
