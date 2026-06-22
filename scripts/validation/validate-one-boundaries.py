#!/usr/bin/env python3
"""Deterministic, read-only VANTARIS ONE architecture boundary scanner."""
from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SCANNER_NAME = "VANTARIS_ONE_BOUNDARY_SCANNER"
SCANNER_VERSION = "1.0.0"
SEVERITIES = ["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW", "REVIEW"]
CATEGORIES = [
    "Registry integrity",
    "Forbidden imports",
    "Cross-module persistence",
    "API namespace ownership",
    "Authentication classification",
    "Permission guards",
    "Route/package alignment",
    "Package state model",
    "Ownership invariants",
    "Idempotency declarations",
    "Audit declarations",
]
SKIP_PARTS = {".git", "node_modules", "dist", "build", "coverage", "__pycache__", ".pytest_cache", ".runtime"}
SCAN_ROOTS = [
    "AN_VANTARIS_IBMS-backend/src",
    "AN_VANTARIS_IBMS-frontend/src",
    "AN_VANTARIS_ONE",
    "contracts",
    "scripts",
    "deployment",
]
PUBLIC_ENDPOINTS = {
    ("/api/did/login", "POST"),
    ("/api/did/challenge", "GET"),
}
MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
CONTROL_WORDS = {"command", "reconnect", "replay", "switch", "train", "deploy", "approve", "execute", "export", "verify"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "strict"), default="baseline")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--root", default=None)
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def source_files(root: Path, suffixes: Sequence[str]) -> Iterable[Path]:
    for base_name in SCAN_ROOTS:
        base = root / base_name
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            yield path


def finding(
    rule_id: str,
    severity: str,
    status: str,
    path: str,
    line: Optional[int],
    symbol: str,
    message: str,
    evidence: str,
    package_id: str,
    owning_module: str,
    remediation_gate: str,
    category: str,
) -> Dict[str, Any]:
    return {
        "ruleId": rule_id,
        "severity": severity,
        "status": status,
        "path": path,
        "line": line,
        "symbol": symbol,
        "message": message,
        "evidence": evidence,
        "packageId": package_id,
        "owningModule": owning_module,
        "exceptionId": None,
        "remediationGate": remediation_gate,
        "_category": category,
    }


def validate_exceptions(doc: Dict[str, Any], root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    rows = doc.get("exceptions")
    errors: List[str] = []
    if not isinstance(rows, list):
        return [], ["exceptions registry must contain an exceptions array"]
    required = {
        "exceptionId", "ruleId", "exactPath", "exactPattern", "rationale", "owner",
        "status", "expiresByPolicy", "compensatingControl", "removalGate",
    }
    seen = set()
    allowed_milestones = {
        "REMOVE_AFTER_P1_ENFORCEMENT",
        "REMOVE_AFTER_ASSET_GRAPH_MIGRATION",
        "REMOVE_AFTER_WORK_MANAGEMENT_MIGRATION",
        "REMOVE_AFTER_EVIDENCE_CENTER_MIGRATION",
        "REMOVE_AFTER_UFMS_ADAPTER_MIGRATION",
    }
    for row in rows:
        missing = required - set(row) if isinstance(row, dict) else required
        if missing:
            errors.append(f"exception missing fields: {sorted(missing)}")
            continue
        exception_id = row["exceptionId"]
        if exception_id in seen:
            errors.append(f"duplicate exceptionId: {exception_id}")
        seen.add(exception_id)
        if row["status"] != "LEGACY_EXCEPTION":
            errors.append(f"{exception_id}: invalid status")
        if row["expiresByPolicy"] not in allowed_milestones:
            errors.append(f"{exception_id}: invalid expiresByPolicy")
        if any(token in row["exactPath"] or token in row["exactPattern"] for token in ("*", "?", "[", "]")):
            errors.append(f"{exception_id}: wildcard exception is prohibited")
        if not (root / row["exactPath"]).is_file():
            errors.append(f"{exception_id}: exactPath does not exist")
        if not str(row["exactPattern"]).strip():
            errors.append(f"{exception_id}: exactPattern is empty")
        elif (root / row["exactPath"]).is_file():
            try:
                if row["exactPattern"] not in (root / row["exactPath"]).read_text(encoding="utf-8"):
                    errors.append(f"{exception_id}: exactPattern is not present in exactPath")
            except UnicodeDecodeError:
                errors.append(f"{exception_id}: exactPath is not UTF-8 text")
    return rows, errors


def apply_exceptions(findings: List[Dict[str, Any]], exceptions: List[Dict[str, Any]]) -> None:
    index = {(row["ruleId"], row["exactPath"], row["exactPattern"]): row for row in exceptions}
    for item in findings:
        key = (item["ruleId"], item["path"], item["symbol"])
        row = index.get(key)
        if row:
            item["status"] = "LEGACY_EXCEPTION"
            item["exceptionId"] = row["exceptionId"]


def decorator_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return decorator_name(node.func)
    return ""


def literal_strings(node: ast.AST) -> List[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        result: List[str] = []
        for child in node.elts:
            result.extend(literal_strings(child))
        return result
    return []


def discover_routes(root: Path) -> List[Dict[str, Any]]:
    routes: List[Dict[str, Any]] = []
    api_root = root / "AN_VANTARIS_IBMS-backend/src/api"
    if not api_root.exists():
        return routes
    for path in sorted(api_root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            route_paths: List[Tuple[str, List[str], int]] = []
            decorator_names = []
            permissions: List[str] = []
            for dec in node.decorator_list:
                decorator_names.append(decorator_name(dec))
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == "route":
                    if not dec.args:
                        continue
                    paths = literal_strings(dec.args[0])
                    methods = ["GET"]
                    for kw in dec.keywords:
                        if kw.arg == "methods":
                            methods = literal_strings(kw.value) or methods
                    for route_path in paths:
                        route_paths.append((route_path, [m.upper() for m in methods], getattr(dec, "lineno", node.lineno)))
                if isinstance(dec, ast.Call) and decorator_name(dec).startswith("require_"):
                    for arg in dec.args:
                        permissions.extend(literal_strings(arg))
            body_source = ast.get_source_segment(path.read_text(encoding="utf-8"), node) or ""
            for route_path, methods, line in route_paths:
                full = "/api" + route_path if not route_path.startswith("/api/") else route_path
                routes.append({
                    "path": full,
                    "rawPath": route_path,
                    "methods": methods,
                    "file": rel(root, path),
                    "line": line,
                    "symbol": node.name,
                    "decorators": decorator_names,
                    "permissions": permissions,
                    "body": body_source,
                })
    return routes


def path_matches(path: str, pattern: str) -> bool:
    if "*" in pattern:
        return fnmatch.fnmatch(path, pattern)
    return path == pattern or path.startswith(pattern.rstrip("/") + "/")


def api_owner_for_route(route: str, api_rows: List[Dict[str, Any]]) -> Tuple[str, Optional[Dict[str, Any]]]:
    target = sorted(api_rows, key=lambda row: len(row["namespace"]), reverse=True)
    for row in target:
        if route == row["namespace"] or route.startswith(row["namespace"] + "/"):
            return "TARGET", row
    legacy_matches = []
    for row in api_rows:
        for legacy in row.get("legacyMappings", []):
            if path_matches(route, legacy):
                legacy_matches.append((len(legacy.replace("*", "")), row))
    if legacy_matches:
        legacy_matches.sort(key=lambda item: item[0], reverse=True)
        return "LEGACY", legacy_matches[0][1]
    return "UNKNOWN", None


def scan_imports(root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    forbidden_tokens = ("ufms", "an_vantaris_edge", "an_vantaris_link")
    for path in source_files(root, (".py", ".ts", ".js", ".tsx", ".jsx")):
        relative = rel(root, path)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, text in enumerate(lines, 1):
            stripped = text.strip()
            executable_import = (
                stripped.startswith(("from ", "import "))
                or re.match(r"^import\s+.+\s+from\s+['\"]", stripped)
                or "require(" in stripped
            )
            if not executable_import:
                continue
            lowered = stripped.lower()
            if any(token in lowered for token in forbidden_tokens):
                findings.append(finding(
                    "A4-BND-001", "P0_CRITICAL", "VIOLATION", relative, number,
                    stripped, "Cross-product runtime import detected.", stripped,
                    "", "", "REMOVE_DIRECT_RUNTIME_IMPORT", "Forbidden imports",
                ))
    return findings


def scan_persistence(root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for path in source_files(root, (".py",)):
        relative = rel(root, path)
        if "/src/" not in relative:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            continue
        parts = relative.split("/")
        try:
            src_index = parts.index("src")
            owner_segment = parts[src_index + 1].lower()
        except (ValueError, IndexError):
            continue
        for node in ast.walk(tree):
            module = ""
            line = getattr(node, "lineno", None)
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
            if not module.startswith("src."):
                continue
            segments = module.split(".")
            if len(segments) < 3:
                continue
            imported_owner = segments[1].lower()
            persistence = any(token in segments for token in ("models", "dao", "repository", "database", "schema", "migrations"))
            if persistence and imported_owner != owner_segment and owner_segment not in {"api", "common", "tests"}:
                findings.append(finding(
                    "A4-BND-002", "REVIEW", "REVIEW", relative, line, module,
                    "Possible cross-module persistence import requires ownership review.", module,
                    "", "", "P1_OWNERSHIP_ENFORCEMENT", "Cross-module persistence",
                ))
    legacy_model = root / "AN_VANTARIS_IBMS-backend/src/Iot/models.py"
    if legacy_model.is_file():
        text = legacy_model.read_text(encoding="utf-8")
        line = next((i for i, value in enumerate(text.splitlines(), 1) if "class IMSDevice" in value), None)
        findings.append(finding(
            "A4-BND-002", "P0_CRITICAL", "VIOLATION", rel(root, legacy_model), line, "IMSDevice",
            "Legacy Device model combines canonical identity and EDGE connector concerns.",
            "class IMSDevice persists protocol/connect_config and identity fields",
            "PKG-ASSET-GRAPH", "ONE Asset Graph", "REMOVE_AFTER_ASSET_GRAPH_MIGRATION",
            "Cross-module persistence",
        ))
    return findings


def scan_routes(root: Path, routes: List[Dict[str, Any]], api_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for route in routes:
        classification, api = api_owner_for_route(route["path"], api_rows)
        package_id = api.get("packageId", "") if api else ""
        owner = api.get("owningModule", "") if api else ""
        if classification == "LEGACY":
            findings.append(finding(
                "A4-BND-004", "P2_MEDIUM", "LEGACY_DEBT", route["file"], route["line"], route["symbol"],
                f"Legacy route {route['path']} maps to target namespace {api['namespace']}.",
                f"{','.join(route['methods'])} {route['path']}", package_id, owner,
                "P1_API_NAMESPACE_MIGRATION", "API namespace ownership",
            ))
        elif classification == "UNKNOWN":
            findings.append(finding(
                "A4-BND-004", "REVIEW", "REVIEW", route["file"], route["line"], route["symbol"],
                f"Route {route['path']} has no registry namespace or legacy mapping.",
                f"{','.join(route['methods'])} {route['path']}", "", "",
                "P0_API_NAMESPACE_FREEZE", "API namespace ownership",
            ))

        authenticated = "jwt_required" in route["decorators"]
        guarded = any(name.startswith("require_") for name in route["decorators"])
        for method in route["methods"]:
            explicit_public = (route["path"], method) in PUBLIC_ENDPOINTS
            control = method in MUTATION_METHODS or any(word in route["path"].lower() for word in CONTROL_WORDS)
            if explicit_public:
                auth_class = "EXPLICITLY_PUBLIC"
            elif authenticated:
                auth_class = "AUTHENTICATED"
            else:
                auth_class = "UNCLASSIFIED"
                severity = "P2_MEDIUM" if method == "OPTIONS" else "P1_HIGH"
                findings.append(finding(
                    "A4-BND-006", severity, "LEGACY_DEBT", route["file"], route["line"], route["symbol"],
                    f"{method} {route['path']} has no explicit authentication classification.",
                    auth_class, package_id, owner, "P1_GOVERNANCE_SECURITY_ENFORCEMENT",
                    "Authentication classification",
                ))

            if control and not explicit_public:
                if guarded:
                    guard_class = "GUARDED"
                elif authenticated:
                    guard_class = "AUTH_ONLY"
                    findings.append(finding(
                        "A4-BND-007", "P1_HIGH", "LEGACY_DEBT", route["file"], route["line"], route["symbol"],
                        f"{method} {route['path']} is authenticated but lacks an action permission guard.",
                        guard_class, package_id, owner, "P1_BACKEND_GUARD_ENFORCEMENT",
                        "Permission guards",
                    ))
                else:
                    guard_class = "UNGUARDED"
                    severity = "P1_HIGH"
                    findings.append(finding(
                        "A4-BND-007", severity, "LEGACY_DEBT", route["file"], route["line"], route["symbol"],
                        f"{method} {route['path']} lacks authentication and action permission guards.",
                        guard_class, package_id, owner, "P1_BACKEND_GUARD_ENFORCEMENT",
                        "Permission guards",
                    ))
                body_lower = route["body"].lower()
                idem_declared = "idempotency" in body_lower or "idempotency-key" in body_lower
                if not idem_declared:
                    findings.append(finding(
                        "A4-BND-018", "P1_HIGH", "LEGACY_DEBT", route["file"], route["line"], route["symbol"],
                        f"{method} {route['path']} has no statically discoverable idempotency declaration.",
                        "NOT_DECLARED", package_id, owner, "P0_ADAPTER_AND_COMMAND_CONTRACTS",
                        "Idempotency declarations",
                    ))
                audit_declared = any(token in body_lower for token in ("log_sensitive_api", "auditrecord", "audit_record", "audit_event"))
                if not audit_declared:
                    findings.append(finding(
                        "A4-BND-019", "P1_HIGH", "LEGACY_DEBT", route["file"], route["line"], route["symbol"],
                        f"{method} {route['path']} has no statically discoverable AuditRecord declaration.",
                        "NOT_DECLARED", package_id, owner, "P0_AUDIT_CONTRACT",
                        "Audit declarations",
                    ))
    return findings


def extract_frontend_routes(root: Path) -> Dict[str, Dict[str, Any]]:
    path = root / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts"
    result: Dict[str, Dict[str, Any]] = {}
    if not path.is_file():
        return result
    lines = path.read_text(encoding="utf-8").splitlines()
    current = None
    for number, line in enumerate(lines, 1):
        match = re.search(r"path:\s*['\"]([^'\"]+)['\"]", line)
        if match:
            current = match.group(1)
            result[current] = {"line": number, "permission": False}
        if current and "permissions:" in line:
            result[current]["permission"] = True
    return result


def scan_frontend(root: Path, package_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    routes = extract_frontend_routes(root)
    registry_routes = {}
    for pkg in package_rows:
        for route in pkg.get("routes", []):
            registry_routes[route] = pkg
    ignored = {"/", "/login", "/403", "/forbidden", "/:pathMatch(.*)*"}
    for route, meta in sorted(routes.items()):
        if route in ignored:
            continue
        pkg = registry_routes.get(route)
        if not pkg:
            findings.append(finding(
                "A4-BND-016", "P1_HIGH", "LEGACY_DEBT",
                "AN_VANTARIS_IBMS-frontend/src/router/routes.ts", meta["line"], route,
                "Frontend route is absent from the frozen package registry.",
                route, "", "", "P1_UCONSOLE_ENFORCEMENT_ALIGNMENT", "Route/package alignment",
            ))
        if not meta["permission"]:
            findings.append(finding(
                "A4-BND-016", "P1_HIGH", "LEGACY_DEBT",
                "AN_VANTARIS_IBMS-frontend/src/router/routes.ts", meta["line"], route,
                "Frontend route has no declared permission metadata.",
                route, pkg.get("packageId", "") if pkg else "", pkg.get("semanticOwner", "") if pkg else "",
                "P1_UCONSOLE_ENFORCEMENT_ALIGNMENT", "Route/package alignment",
            ))
    for route, pkg in sorted(registry_routes.items()):
        if route not in routes:
            findings.append(finding(
                "A4-BND-016", "P2_MEDIUM", "LEGACY_DEBT",
                "AN_VANTARIS_ONE/registries/package-registry.v1.json", None, route,
                "Frozen package route is not yet present in the frontend router.",
                f"{pkg['packageId']} -> {route}", pkg["packageId"], pkg["semanticOwner"],
                "P1_UCONSOLE_ENFORCEMENT_ALIGNMENT", "Route/package alignment",
            ))
    guard_path = root / "AN_VANTARIS_IBMS-frontend/src/router/guards.ts"
    if guard_path.is_file():
        text = guard_path.read_text(encoding="utf-8")
        if re.search(r"function\s+hasPermission\b[\s\S]{0,200}return\s+true", text):
            line = next((i for i, value in enumerate(text.splitlines(), 1) if "function hasPermission" in value), None)
            findings.append(finding(
                "A4-BND-008", "P1_HIGH", "LEGACY_DEBT", rel(root, guard_path), line, "hasPermission",
                "Frontend permission guard currently allows every permission request.",
                "hasPermission(...) returns true", "PKG-UCONSOLE", "UConsole",
                "P1_UCONSOLE_ENFORCEMENT_ALIGNMENT", "Route/package alignment",
            ))
    return findings


def scan_package_states(root: Path, package_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    required = {"installed", "entitled", "enabled", "visible", "healthy"}
    for pkg in package_rows:
        dimensions = pkg.get("stateDimensions", {})
        if set(dimensions) != required or len(set(dimensions.values())) < 2:
            findings.append(finding(
                "A4-BND-017", "P0_CRITICAL", "VIOLATION",
                "AN_VANTARIS_ONE/registries/package-registry.v1.json", None, pkg.get("packageId", ""),
                "Frozen package state dimensions are missing or collapsed.", json.dumps(dimensions, sort_keys=True),
                pkg.get("packageId", ""), pkg.get("semanticOwner", ""),
                "P0_PACKAGE_STATE_MODEL", "Package state model",
            ))
    runtime = root / "AN_VANTARIS_IBMS-backend/src/console/module_package_registry.py"
    if runtime.is_file():
        text = runtime.read_text(encoding="utf-8")
        if all(f'"{key}"' in text for key in ("installed", "entitled", "enabled", "visible")) and "health" not in text.lower():
            findings.append(finding(
                "A4-BND-017", "P2_MEDIUM", "LEGACY_DEBT", rel(root, runtime), None, "_package_record",
                "Legacy package skeleton separates four access states but has no independent package health dimension.",
                "installed/entitled/enabled/visible present; healthy absent",
                "PKG-UCONSOLE", "UConsole", "P1_PACKAGE_ENFORCEMENT_RUNTIME", "Package state model",
            ))
    return findings


def line_for(text: str, needle: str) -> Optional[int]:
    return next((i for i, value in enumerate(text.splitlines(), 1) if needle in value), None)


def scan_ownership(root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    checks = [
        ("A4-BND-011", "P0_CRITICAL", "AN_VANTARIS_IBMS-backend/src/umms/umms_provider.py", "_work_order",
         "UMMS skeleton defines generic WorkOrder records outside ONE Work Management.",
         "PKG-UMMS", "UMMS", "REMOVE_AFTER_WORK_MANAGEMENT_MIGRATION"),
        ("A4-BND-012", "P0_CRITICAL", "AN_VANTARIS_IBMS-backend/src/ucde/evidence_provider.py", "_base_records",
         "UCDE skeleton provides EvidenceRecord data outside Evidence Center.",
         "PKG-UCDE", "UCDE", "REMOVE_AFTER_EVIDENCE_CENTER_MIGRATION"),
        ("A4-BND-009", "P0_CRITICAL", "AN_VANTARIS_IBMS-backend/src/reports/reports_audit_store.py", "append_audit_record",
         "Reports writes local audit persistence outside Governance & Security.",
         "PKG-REPORTS", "Reports", "REMOVE_AFTER_P1_ENFORCEMENT"),
    ]
    for rule, severity, relative, symbol, message, package, owner, gate in checks:
        path = root / relative
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if symbol in text:
                findings.append(finding(
                    rule, severity, "VIOLATION", relative, line_for(text, f"def {symbol}"), symbol,
                    message, f"{symbol} statically present", package, owner, gate, "Ownership invariants",
                ))
    adapter = root / "AN_VANTARIS_ONE/platform/one-adapter/module.manifest.draft.json"
    if adapter.is_file():
        try:
            status = load_json(adapter).get("status")
        except Exception:
            status = None
        if status != "cancelled-a1":
            findings.append(finding(
                "A4-BND-001", "P0_CRITICAL", "VIOLATION", rel(root, adapter), None, "one-adapter",
                "Standalone one-adapter is not marked cancelled.", str(status), "", "",
                "PERMANENTLY_STOP_STANDALONE_ADAPTER", "Ownership invariants",
            ))
    allowed_schema_roots = (
        "contracts/",
        "AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts/schemas/",
    )
    for path in source_files(root, (".json",)):
        relative = rel(root, path)
        if path.name.endswith(".schema.json") and not relative.startswith(allowed_schema_roots):
            findings.append(finding(
                "A4-BND-005", "P0_CRITICAL", "VIOLATION", relative, None, path.name,
                "Canonical/shared schema artifact is declared outside Contracts.",
                relative, "", "", "MOVE_SCHEMA_TO_CONTRACTS", "Ownership invariants",
            ))
    specialized_checks = [
        (
            "A4-BND-013", "AN_VANTARIS_IBMS-backend/src/ucore",
            ("class Asset", "__tablename__", "db.Model"), ("asset", "site", "building", "device", "point"),
            "UCore appears to persist canonical asset data.", "PKG-UCORE", "UCore",
            "REMOVE_AFTER_ASSET_GRAPH_MIGRATION",
        ),
        (
            "A4-BND-010", "AN_VANTARIS_IBMS-backend/src/uedge",
            ("WorkOrder", "FaultCase", "MaintenancePlan", "DecisionCase"), (),
            "EDGE projection code appears to implement a business lifecycle.", "PKG-EDGE", "AN_VANTARIS_EDGE",
            "REMOVE_BUSINESS_LIFECYCLE_FROM_EDGE",
        ),
        (
            "A4-BND-014", "AN_VANTARIS_IBMS-backend/src/data_modeling",
            ("db.session.add", "db.session.delete", "db.session.commit"), ("WorkOrder", "Asset", "FaultCase", "EvidenceRecord"),
            "AI/modeling code appears to mutate canonical business state directly.", "PKG-NEXUS-AI", "Nexus AI",
            "P3_AI_APPROVAL_AND_COMMAND_BOUNDARY",
        ),
    ]
    for rule, base_name, primary_tokens, context_tokens, message, package, owner, gate in specialized_checks:
        base = root / base_name
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            primary_hit = next((token for token in primary_tokens if token in text), None)
            context_ok = not context_tokens or any(token in text for token in context_tokens)
            if primary_hit and context_ok:
                findings.append(finding(
                    rule, "P0_CRITICAL", "VIOLATION", rel(root, path), line_for(text, primary_hit),
                    primary_hit, message, primary_hit, package, owner, gate, "Ownership invariants",
                ))
    return findings


def registry_integrity(root: Path) -> Tuple[bool, str]:
    validator = root / "scripts/validation/validate-one-registries.py"
    if not validator.is_file():
        return False, "registry validator missing"
    completed = subprocess.run(
        [sys.executable, str(validator)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0, completed.stdout.strip() or completed.stderr.strip()


def category_result(findings: List[Dict[str, Any]], category: str) -> str:
    rows = [row for row in findings if row["_category"] == category]
    if any(row["status"] == "VIOLATION" and row["severity"] == "P0_CRITICAL" for row in rows):
        return "FAIL"
    if rows:
        return "WARN"
    return "PASS"


def blocking(findings: List[Dict[str, Any]], mode: str, exception_errors: List[str], registry_ok: bool) -> bool:
    if exception_errors or not registry_ok:
        return True
    for row in findings:
        if row["status"] == "LEGACY_EXCEPTION":
            continue
        if mode == "baseline" and row["severity"] == "P0_CRITICAL" and row["status"] == "VIOLATION":
            return True
        if mode == "strict" and row["severity"] in {"P0_CRITICAL", "P1_HIGH"} and row["status"] in {"VIOLATION", "LEGACY_DEBT"}:
            return True
    return False


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    registry_paths = {
        "objects": root / "contracts/registry/canonical-objects.v1.json",
        "contracts": root / "contracts/registry/contract-namespaces.v1.json",
        "packages": root / "AN_VANTARIS_ONE/registries/package-registry.v1.json",
        "permissions": root / "AN_VANTARIS_ONE/registries/permission-registry.v1.json",
        "apis": root / "AN_VANTARIS_ONE/registries/api-namespace-registry.v1.json",
        "exceptions": root / "AN_VANTARIS_ONE/registries/boundary-exceptions.v1.json",
    }
    try:
        registries = {key: load_json(path) for key, path in registry_paths.items()}
    except Exception as exc:
        payload = {
            "scannerName": SCANNER_NAME, "scannerVersion": SCANNER_VERSION, "mode": args.mode,
            "result": "FAIL", "counts": {}, "categoryResults": {"Registry integrity": "FAIL"},
            "findings": [], "errors": [str(exc)],
        }
        print(json.dumps(payload, indent=2, sort_keys=True) if args.format == "json" else f"[ONE BOUNDARY VALIDATION]\nRegistry integrity: FAIL\n{exc}\nONE_BOUNDARY_VALIDATION_FAIL")
        return 1

    exceptions, exception_errors = validate_exceptions(registries["exceptions"], root)
    registry_ok, registry_evidence = registry_integrity(root)
    api_rows = registries["apis"]["apiNamespaces"]
    package_rows = registries["packages"]["packages"]

    routes = discover_routes(root)
    findings: List[Dict[str, Any]] = []
    findings.extend(scan_imports(root))
    findings.extend(scan_persistence(root))
    findings.extend(scan_routes(root, routes, api_rows))
    findings.extend(scan_frontend(root, package_rows))
    findings.extend(scan_package_states(root, package_rows))
    findings.extend(scan_ownership(root))
    apply_exceptions(findings, exceptions)
    findings.sort(key=lambda row: (
        SEVERITIES.index(row["severity"]) if row["severity"] in SEVERITIES else 99,
        row["ruleId"], row["path"], row["line"] if row["line"] is not None else -1, row["symbol"],
    ))

    is_blocking = blocking(findings, args.mode, exception_errors, registry_ok)
    counts = {severity: sum(1 for row in findings if row["severity"] == severity) for severity in SEVERITIES}
    counts["LEGACY_EXCEPTION"] = sum(1 for row in findings if row["status"] == "LEGACY_EXCEPTION")
    counts["LEGACY_DEBT"] = sum(1 for row in findings if row["status"] == "LEGACY_DEBT")
    category_results = {category: category_result(findings, category) for category in CATEGORIES}
    category_results["Registry integrity"] = "PASS" if registry_ok and not exception_errors else "FAIL"
    public_findings = [{key: value for key, value in row.items() if key != "_category"} for row in findings]
    result = "FAIL" if is_blocking else "PASS"
    payload = {
        "scannerName": SCANNER_NAME,
        "scannerVersion": SCANNER_VERSION,
        "mode": args.mode,
        "result": result,
        "counts": counts,
        "categoryResults": category_results,
        "findings": public_findings,
    }
    if exception_errors:
        payload["exceptionErrors"] = exception_errors
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("[ONE BOUNDARY VALIDATION]")
        for category in CATEGORIES:
            print(f"{category}: {category_results[category]}")
        print("")
        for key in SEVERITIES + ["LEGACY_EXCEPTION", "LEGACY_DEBT"]:
            print(f"{key}: {counts[key]}")
        if exception_errors:
            print("")
            for item in exception_errors:
                print(f"EXCEPTION_ERROR: {item}")
        print("")
        notable = [
            row for row in public_findings
            if row["severity"] == "P0_CRITICAL"
            or row["status"] == "LEGACY_EXCEPTION"
            or row["status"] == "VIOLATION"
        ]
        for row in notable:
            location = f"{row['path']}:{row['line']}" if row["line"] is not None else row["path"]
            print(f"{row['severity']} {row['status']} {row['ruleId']} {location} {row['symbol']} - {row['message']}")
        omitted = len(public_findings) - len(notable)
        if omitted:
            print(f"Additional non-blocking findings: {omitted} (use --format json for full detail)")
        if not is_blocking:
            print("ONE_BOUNDARY_BASELINE_PASS" if args.mode == "baseline" else "ONE_BOUNDARY_STRICT_PASS")
        else:
            print("ONE_BOUNDARY_VALIDATION_FAIL")
    return 1 if is_blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
