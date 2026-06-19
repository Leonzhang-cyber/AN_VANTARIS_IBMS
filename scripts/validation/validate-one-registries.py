#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "objects": ROOT / "contracts/registry/canonical-objects.v1.json",
    "contracts": ROOT / "contracts/registry/contract-namespaces.v1.json",
    "packages": ROOT / "AN_VANTARIS_ONE/registries/package-registry.v1.json",
    "permissions": ROOT / "AN_VANTARIS_ONE/registries/permission-registry.v1.json",
    "apis": ROOT / "AN_VANTARIS_ONE/registries/api-namespace-registry.v1.json",
}
EXPECTED = {
    "objects": ("VANTARIS_ONE_CANONICAL_OBJECT_REGISTRY", "objects"),
    "contracts": ("VANTARIS_ONE_CONTRACT_NAMESPACE_REGISTRY", "namespaces"),
    "packages": ("VANTARIS_ONE_PACKAGE_REGISTRY", "packages"),
    "permissions": ("VANTARIS_ONE_PERMISSION_REGISTRY", "permissions"),
    "apis": ("VANTARIS_ONE_API_NAMESPACE_REGISTRY", "apiNamespaces"),
}
errors = []
data = {}

def error(message):
    errors.append(message)

def unique(rows, key, label):
    seen = set()
    for row in rows:
        value = row.get(key)
        if value in seen:
            error(f"duplicate {label}: {value}")
        seen.add(value)
    return seen

for key, path in FILES.items():
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")
        continue
    try:
        data[key] = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        error(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        continue
    expected_name, collection = EXPECTED[key]
    doc = data[key]
    if doc.get("registryName") != expected_name:
        error(f"{key}: invalid registryName")
    if not doc.get("registryVersion"):
        error(f"{key}: missing registryVersion")
    if doc.get("generatedAtPolicy") != "STATIC_ARCHITECTURE_BASELINE":
        error(f"{key}: invalid generatedAtPolicy")
    if doc.get("authority") != "ONE-PLAN-A4" or doc.get("status") != "FROZEN_FOR_IMPLEMENTATION":
        error(f"{key}: invalid authority/status")
    if not isinstance(doc.get(collection), list):
        error(f"{key}: missing collection {collection}")

if errors:
    print("[ONE REGISTRY VALIDATION]")
    for item in errors:
        print(f"FAIL: {item}")
    print("ONE_REGISTRY_FOUNDATION_FAIL")
    sys.exit(1)

objects = data["objects"]["objects"]
contracts = data["contracts"]["namespaces"]
packages = data["packages"]["packages"]
permissions = data["permissions"]["permissions"]
apis = data["apis"]["apiNamespaces"]

object_names = unique(objects, "objectName", "canonical object")
contract_names = unique(contracts, "namespace", "contract namespace")
package_ids = unique(packages, "packageId", "package ID")
permission_names = unique(permissions, "permission", "permission")
api_names = unique(apis, "namespace", "API namespace")

for obj in objects:
    if obj.get("namespace") not in contract_names:
        error(f"{obj.get('objectName')}: unknown contract namespace {obj.get('namespace')}")
    if not isinstance(obj.get("semanticOwner"), str) or not obj["semanticOwner"].strip():
        error(f"{obj.get('objectName')}: semanticOwner must be exactly one non-empty string")
    if not isinstance(obj.get("systemOfRecord"), str) or not obj["systemOfRecord"].strip():
        error(f"{obj.get('objectName')}: systemOfRecord must be exactly one non-empty string")

graph = {}
for pkg in packages:
    graph[pkg["packageId"]] = list(pkg.get("dependencies", []))
    for dep in graph[pkg["packageId"]]:
        if dep not in package_ids:
            error(f"{pkg['packageId']}: unknown dependency {dep}")
    for permission in pkg.get("permissions", []):
        if permission not in permission_names:
            error(f"{pkg['packageId']}: unknown permission {permission}")
    for api in pkg.get("publicApiNamespaces", []):
        if api not in api_names:
            error(f"{pkg['packageId']}: unknown API namespace {api}")
    dims = pkg.get("stateDimensions", {})
    required_dims = {"installed", "entitled", "enabled", "visible", "healthy"}
    if set(dims) != required_dims or len(set(dims.values())) < 2:
        error(f"{pkg['packageId']}: package states are missing or collapsed")

visiting = set()
visited = set()
def visit(node, trail):
    if node in visiting:
        error("package dependency cycle: " + " -> ".join(trail + [node]))
        return
    if node in visited:
        return
    visiting.add(node)
    for dep in graph.get(node, []):
        visit(dep, trail + [node])
    visiting.remove(node)
    visited.add(node)
for package_id in graph:
    visit(package_id, [])

for api in apis:
    if api.get("packageId") not in package_ids:
        error(f"{api.get('namespace')}: unknown packageId {api.get('packageId')}")
    for contract in api.get("contractNamespaces", []):
        if contract not in contract_names:
            error(f"{api.get('namespace')}: unknown contract namespace {contract}")

pattern = re.compile(r"^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$")
for permission in permissions:
    if not pattern.fullmatch(str(permission.get("permission", ""))):
        error(f"invalid permission format: {permission.get('permission')}")

ufms = next((p for p in packages if p.get("packageId") == "PKG-UFMS-INTEGRATION"), None)
if not ufms or ufms.get("packageClass") != "EXTERNAL_PRODUCT_INTEGRATION":
    error("PKG-UFMS-INTEGRATION must be EXTERNAL_PRODUCT_INTEGRATION")
for package_id in package_ids:
    normalized = package_id.lower().replace("_", "-")
    if "one-adapter" in normalized or normalized in {"pkg-adapter", "one-adapter"}:
        error(f"forbidden standalone adapter package: {package_id}")

serialized = json.dumps(data, sort_keys=True).lower()
for forbidden in ["http://", "https://", "localhost", "127.0.0.1"]:
    if forbidden in serialized:
        error(f"forbidden endpoint/environment value found: {forbidden}")

expected_owners = {
    "Asset": ("ONE Asset Graph", "ONE Asset Graph"),
    "Device": ("ONE Asset Graph", "ONE Asset Graph"),
    "Point": ("ONE Asset Graph", "ONE Asset Graph"),
    "WorkOrder": ("ONE Work Management", "ONE Work Management"),
    "EvidenceRecord": ("Evidence Center", "Evidence Center"),
    "AuditRecord": ("Governance & Security", "Governance & Security Audit Service"),
    "FaultCase": ("UFMS", "UFMS"),
}
by_name = {obj["objectName"]: obj for obj in objects}
for name, (owner, sor) in expected_owners.items():
    obj = by_name.get(name)
    if not obj:
        error(f"missing ownership invariant object: {name}")
    elif obj.get("semanticOwner") != owner or obj.get("systemOfRecord") != sor:
        error(f"ownership contradiction for {name}")

checks = [
    ("Canonical objects", not any("canonical object" in e or "object:" in e for e in errors)),
    ("Contract namespaces", not any("contract namespace" in e for e in errors)),
    ("Packages", not any("package" in e.lower() and "dependency cycle" not in e for e in errors)),
    ("Permissions", not any("permission" in e for e in errors)),
    ("API namespaces", not any("API namespace" in e or "unknown API" in e for e in errors)),
    ("Dependency graph", not any("dependency" in e for e in errors)),
    ("Ownership invariants", not any("ownership" in e for e in errors)),
    ("UFMS boundary", not any("UFMS" in e or "adapter package" in e for e in errors)),
]
print("[ONE REGISTRY VALIDATION]")
for label, passed in checks:
    print(f"{label}: {'PASS' if passed else 'FAIL'}")
if errors:
    for item in errors:
        print(f"FAIL: {item}")
    print("ONE_REGISTRY_FOUNDATION_FAIL")
    sys.exit(1)
print("ONE_REGISTRY_FOUNDATION_PASS")
