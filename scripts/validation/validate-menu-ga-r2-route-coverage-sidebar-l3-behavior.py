#!/usr/bin/env python3
"""Validate MENU-GA-R2 route coverage and Sidebar/L3 behavior audit."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_MENU_GA_R2_ROUTE_COVERAGE_SIDEBAR_L3_BEHAVIOR_AUDIT_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/MENU_GA_R2.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r2/menu-ga-r2.registry.json"
EVIDENCE = ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r2/menu-ga-r2.evidence.json"
VALIDATION = ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r2/menu-ga-r2.validation.json"
VALIDATOR = ROOT / "scripts/validation/validate-menu-ga-r2-route-coverage-sidebar-l3-behavior.py"

STATIC_MENU = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts"
TYPES = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/types.ts"
APP_LAYOUT = ROOT / "AN_VANTARIS_IBMS-frontend/src/components/AppLayout.vue"
ROUTES = ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts"

FLAGS = {
    "frontendMutationAllowed": False,
    "backendMutationAllowed": False,
    "routeMutationAllowed": False,
    "menuMutationAllowed": False,
    "l3SidebarAllowed": False,
    "sshResidueAllowed": False,
    "routeCoverageRequired": True,
    "duplicateMenuIdAllowed": False,
    "duplicateMenuPathAllowed": False,
    "duplicateRoutePathAllowed": False,
    "duplicateRouteNameAllowed": False,
    "duplicateL3IdAllowed": False,
    "dashboardNamingRequired": True,
}
FORBIDDEN_LABELS = ["Mock", "MVP", "Coming soon"]
FORBIDDEN_ROUTE_RESIDUE = [
    "ServerSshApprovalPacket",
    "server-ssh-approval-packet",
    "ssh-approval",
    "SSH Approval Packet",
    "R4 SSH",
    "SERVER_PRECHECK_R4",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(read(path))
    if not isinstance(payload, dict):
        fail(f"JSON root must be object: {path.relative_to(ROOT)}")
    return payload


def extract_static_menu_records(source: str) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    domain_re = re.compile(
        r"\{\s*id:\s*'(?P<id>[^']+)'\s*,\s*label:\s*'(?P<label>[^']+)'\s*,\s*path:\s*'(?P<path>[^']+)'\s*,\s*icon:\s*'(?P<icon>[^']+)'\s*,\s*children:\s*\[(?P<children>.*?)\]\s*,\s*\}",
        re.S,
    )
    child_re = re.compile(
        r"\{\s*id:\s*'(?P<id>[^']+)'\s*,\s*label:\s*'(?P<label>[^']+)'\s*,\s*path:\s*'(?P<path>[^']+)'\s*,\s*status:\s*'(?P<status>[^']+)'\s*,\s*l3:\s*\[(?P<l3>.*?)\](?:,\s*mappedExistingModule:\s*'(?P<mapped>[^']+)')?\s*\}",
        re.S,
    )
    label_re = re.compile(r"'([^']+)'|\"([^\"]+)\"")

    domains: list[dict[str, str]] = []
    children: list[dict[str, Any]] = []
    for match in domain_re.finditer(source):
        domain = {"id": match.group("id"), "label": match.group("label"), "path": match.group("path")}
        domains.append(domain)
        for child in child_re.finditer(match.group("children")):
            l3_labels = [left or right for left, right in label_re.findall(child.group("l3"))]
            children.append(
                {
                    "id": child.group("id"),
                    "label": child.group("label"),
                    "path": child.group("path"),
                    "domainId": domain["id"],
                    "domainLabel": domain["label"],
                    "l3": l3_labels,
                }
            )
    if not domains:
        fail("could not extract L1 domains from static-menu.ts")
    if not children:
        fail("could not extract L2 children from static-menu.ts")
    return domains, children


def slug(label: str, index: int) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"{value}-{index + 1}"


def extract_routes(source: str) -> tuple[list[str], list[str]]:
    paths = re.findall(r"path:\s*'([^']+)'", source)
    names = re.findall(r"name:\s*'([^']+)'", source)
    if not paths:
        fail("could not extract route paths from routes.ts")
    if not names:
        fail("could not extract route names from routes.ts")
    return paths, names


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def main() -> int:
    required = [DOC, REGISTRY, EVIDENCE, VALIDATION, VALIDATOR, STATIC_MENU, TYPES, APP_LAYOUT, ROUTES]
    for path in required:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")
    ok("required MENU-GA-R2 docs, registry, evidence, validation, validator, and read-only source files exist")

    registry = load_json(REGISTRY)
    evidence = load_json(EVIDENCE)
    validation = load_json(VALIDATION)
    for name, payload in (("registry", registry), ("evidence", evidence), ("validation", validation)):
        if PASS not in json.dumps(payload):
            fail(f"PASS marker missing in {name}")
    if PASS not in read(DOC):
        fail("PASS marker missing in document")
    ok("PASS marker exists in document and JSON registry files")

    if registry.get("taskId") != "MENU-GA-R2":
        fail("registry taskId must be MENU-GA-R2")
    if registry.get("sourceTaskId") != "MENU-GA-R1":
        fail("registry sourceTaskId must be MENU-GA-R1")
    if registry.get("mode") != "audit-only":
        fail("registry mode must be audit-only")
    for key, expected in FLAGS.items():
        if registry.get(key) is not expected:
            fail(f"registry {key} must be {expected}")
    ok("registry flags are correct")

    static_text = read(STATIC_MENU)
    types_text = read(TYPES)
    layout_text = read(APP_LAYOUT)
    routes_text = read(ROUTES)

    for phrase in ("fallbackMenuItems", "l3Items"):
        if phrase not in static_text:
            fail(f"static-menu.ts missing {phrase}")
    for phrase in ("AppMenuL3Item", "l3Items?: AppMenuL3Item[]"):
        if phrase not in types_text:
            fail(f"types.ts missing {phrase}")
    for phrase in ("SIDEBAR_COLLAPSED_KEY", "sidebarCollapsed", "activeL3Items", "app-layout__l3-row", ":collapse=\"sidebarCollapsed\""):
        if phrase not in layout_text:
            fail(f"AppLayout.vue missing {phrase}")
    ok("static menu, type model, Sidebar collapse, and content-area L3 behavior are present")

    if "v-for=\"item in activeL3Items\"" not in layout_text:
        fail("L3 items must render from activeL3Items in content area")
    aside_match = re.search(r"<el-aside\b.*?</el-aside>", layout_text, re.S)
    if not aside_match:
        fail("could not isolate Sidebar el-aside template")
    sidebar_template = aside_match.group(0)
    if "activeL3Items" in sidebar_template:
        fail("L3 items are referenced before el-main and may be rendered in Sidebar")
    if "l3Items" in sidebar_template:
        fail("l3Items are referenced in Sidebar template")
    ok("L3 items are not rendered inside Sidebar menu children")

    domains, children = extract_static_menu_records(static_text)
    l1_labels = [item["label"] for item in domains]
    if "Dashboard" not in l1_labels:
        fail("Dashboard must exist as L1")
    if "Home" in l1_labels:
        fail("Home must not be used as L1 label")
    ok("Dashboard exists as L1 and Home is not used as an L1 label")

    menu_ids = [item["id"] for item in domains] + [item["id"] for item in children]
    duplicate_ids = duplicates(menu_ids)
    if duplicate_ids:
        fail(f"duplicate menu ids found: {duplicate_ids}")
    ok("no duplicate menu id in static menu source")

    path_reuse_exceptions = set(map(str, registry.get("routePathReuseExceptions", [])))
    path_to_items: dict[str, list[str]] = defaultdict(list)
    for item in domains + children:
        path_to_items[item["path"]].append(f"{item.get('domainLabel', 'L1')}::{item['label']}")
    unexpected_duplicate_paths = sorted(
        path for path, owners in path_to_items.items() if len(owners) > 1 and path not in path_reuse_exceptions
    )
    if unexpected_duplicate_paths:
        fail(f"duplicate menu paths outside documented reuse exceptions: {unexpected_duplicate_paths}")
    ok("no duplicate menu path outside documented metadata-only reuse exceptions")

    l3_conflicts: list[str] = []
    for child in children:
        ids = [slug(label, index) for index, label in enumerate(child["l3"])]
        for duplicate in duplicates(ids):
            l3_conflicts.append(f"{child['id']}::{duplicate}")
    if l3_conflicts:
        fail(f"duplicate L3 id generation conflicts: {l3_conflicts}")
    ok("no duplicate L3 id generation conflict within any L2")

    route_paths, route_names = extract_routes(routes_text)
    duplicate_route_paths = duplicates(route_paths)
    duplicate_route_names = duplicates(route_names)
    if duplicate_route_paths:
        fail(f"duplicate route paths found: {duplicate_route_paths}")
    if duplicate_route_names:
        fail(f"duplicate route names found: {duplicate_route_names}")
    ok("routes.ts has no duplicate route path or route name")

    route_path_set = set(route_paths)
    allowed_missing = set(map(str, registry.get("allowedRouteCoverageExceptions", [])))
    menu_paths = {item["path"] for item in domains + children}
    missing_routes = sorted(path for path in menu_paths if path not in route_path_set and path not in allowed_missing)
    if missing_routes:
        fail(f"menu paths without matching route path: {missing_routes}")
    ok("every L1/L2 menu path is covered by routes.ts or documented exception")

    for residue in FORBIDDEN_ROUTE_RESIDUE:
        if residue in routes_text:
            fail(f"forbidden R4 / SSH route residue found in routes.ts: {residue}")
    combined = "\n".join([static_text, types_text, layout_text, routes_text])
    for label in FORBIDDEN_LABELS:
        if label in combined:
            fail(f"forbidden label present in MENU-GA-R2 audit scope: {label}")
    allowed_demo_labels = set(map(str, registry.get("allowedScenarioLabels", [])))
    demo_labels = re.findall(r"['\"]([^'\"]*Demo[^'\"]*)['\"]", combined)
    unsupported_demo = sorted(label for label in demo_labels if label not in allowed_demo_labels)
    if unsupported_demo:
        fail(f"unsupported standalone Demo labels present: {unsupported_demo}")
    ok("forbidden R4 / SSH route residue and forbidden labels are absent")

    print(PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
