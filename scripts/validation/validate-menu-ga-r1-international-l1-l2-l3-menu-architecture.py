#!/usr/bin/env python3
"""Validate MENU-GA-R1 international L1/L2/L3 menu architecture."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_MENU_GA_R1_INTERNATIONAL_L1_L2_L3_MENU_ARCHITECTURE_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/MENU_GA_R1.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r1/menu-ga-r1.registry.json"
EVIDENCE = ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r1/menu-ga-r1.evidence.json"
VALIDATION = ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r1/menu-ga-r1.validation.json"
STATIC_MENU = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts"
TYPES = ROOT / "AN_VANTARIS_IBMS-frontend/src/services/menu/types.ts"
APP_LAYOUT = ROOT / "AN_VANTARIS_IBMS-frontend/src/components/AppLayout.vue"
ROUTES = ROOT / "AN_VANTARIS_IBMS-frontend/src/router/routes.ts"

REQUIRED_L1 = {
    "Dashboard",
    "Operations Command",
    "Sites & Spaces",
    "Systems & Assets",
    "Alarms & Events",
    "UFMS - Fault Management",
    "UMMS - Maintenance Management",
    "UESG - Energy & Sustainability",
    "Reports & Compliance",
    "Engineer Workspace",
    "Administration",
}
SCENARIOS = {"UMMS", "UFMS", "UESG", "Airport", "Data Center"}
VENDORS = {"Schneider", "Siemens", "Honeywell", "Johnson Controls"}
FORBIDDEN_TEXT = ["Mock", "MVP", "Coming soon"]
FORBIDDEN_EXECUTION = [
    "import sub" + "process",
    "os." + "system",
    "import so" + "cket",
    "import req" + "uests",
    "para" + "miko",
    "psy" + "copg",
    "py" + "mysql",
    "sqlalchemy." + "create_engine",
    "db.session",
    "methods=[\"POST\"]",
    "methods=[\"PUT\"]",
    "methods=[\"PATCH\"]",
    "methods=[\"DELETE\"]",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def all_l3_items(registry: dict[str, Any]) -> list[Any]:
    result: list[Any] = []
    for domain in as_list(registry.get("menuDomains")):
      for l2 in as_list(domain.get("l2Items")):
        result.extend(as_list(l2.get("l3Items")))
    return result


def l3_label(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("label", ""))
    return ""


def main() -> int:
    for path in [DOC, REGISTRY, EVIDENCE, VALIDATION, STATIC_MENU, TYPES, APP_LAYOUT, ROUTES]:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")
    ok("required MENU-GA-R1 docs, registry, evidence, validation, and frontend files exist")

    registry = json.loads(read(REGISTRY))
    evidence = json.loads(read(EVIDENCE))
    validation = json.loads(read(VALIDATION))
    for name, payload in (("registry", registry), ("evidence", evidence), ("validation", validation)):
        if PASS not in json.dumps(payload):
            fail(f"PASS marker missing in {name}")
    if registry.get("scope") != "MENU_GA_R1":
        fail("registry scope must be MENU_GA_R1")
    if registry.get("homeRenamedToDashboard") is not True:
        fail("homeRenamedToDashboard must be true")
    if registry.get("sidebarCollapseRequired") is not True:
        fail("sidebarCollapseRequired must be true")
    if registry.get("l3InContentAreaOnly") is not True:
        fail("l3InContentAreaOnly must be true")
    if registry.get("leftSidebarLevels") != ["L1", "L2"]:
        fail("leftSidebarLevels must be ['L1', 'L2']")
    if registry.get("contentAreaLevels") != ["L3"]:
        fail("contentAreaLevels must be ['L3']")
    ok("registry top-level L1/L2/L3 menu policy fields are correct")

    domains = as_list(registry.get("menuDomains"))
    labels = {str(domain.get("label")) for domain in domains}
    if "Home" in labels:
        fail("L1 label Home is not allowed")
    if "Dashboard" not in labels:
        fail("L1 Dashboard is required")
    missing_l1 = sorted(REQUIRED_L1 - labels)
    if missing_l1:
        fail(f"missing required L1 labels: {missing_l1}")
    ok("required L1 domains exist and Home is not used as an L1 label")

    scenario_values = set(map(str, as_list(registry.get("scenarioCoverage"))))
    if not SCENARIOS.issubset(scenario_values):
        fail("scenarioCoverage must include UMMS, UFMS, UESG, Airport, and Data Center")
    vendor_text = " ".join(map(str, as_list(registry.get("internationalGaBenchmarkVendors"))))
    for vendor in VENDORS:
        if vendor not in vendor_text:
            fail(f"vendor benchmark missing: {vendor}")
    if registry.get("legacyIbmsMenuMapped") is not True or not registry.get("existingIbmsMapping"):
        fail("legacy IBMS menu mapping is required")
    ok("scenario coverage, vendor benchmark, and legacy IBMS mapping are present")

    for item in all_l3_items(registry):
        if isinstance(item, dict):
            if item.get("contentAreaOnly") is not True:
                fail(f"L3 contentAreaOnly must be true: {item}")
            if item.get("sidebarVisible") is not False:
                fail(f"L3 sidebarVisible must be false: {item}")
        elif not isinstance(item, str):
            fail(f"L3 item must be string shorthand or object: {item}")
    ok("all registry L3 entries are content-area metadata and not Sidebar nodes")

    engineer = next((domain for domain in domains if domain.get("label") == "Engineer Workspace"), None)
    if not engineer:
        fail("Engineer Workspace domain missing")
    server_precheck = next((l2 for l2 in as_list(engineer.get("l2Items")) if l2.get("label") == "Server Precheck"), None)
    if not server_precheck:
        fail("Server Precheck must belong to Engineer Workspace")
    server_l3 = {l3_label(item) for item in as_list(server_precheck.get("l3Items"))}
    for required in ["R1 Environment Audit", "R2 Access Window", "R3 Observation Plan", "R4 SSH Approval Packet"]:
        if required not in server_l3:
            fail(f"Server Precheck L3 missing: {required}")
    ok("Server Precheck R1-R4 is reconciled under Engineer Workspace")

    static_text = read(STATIC_MENU)
    layout_text = read(APP_LAYOUT)
    types_text = read(TYPES)
    for phrase in ["l3Items", "sidebarCollapsed", "localStorage", "app-layout__l3-row", ":collapse=\"sidebarCollapsed\""]:
        if phrase not in static_text + layout_text + types_text:
            fail(f"frontend L3/sidebar implementation phrase missing: {phrase}")
    child_labels = set(re.findall(r"label:\s*'([^']+)'", static_text))
    for l3 in all_l3_items(registry):
        label = l3_label(l3)
        if label in child_labels and not any(label == str(l2.get("label")) for domain in domains for l2 in as_list(domain.get("l2Items"))):
            fail(f"L3 label appears as a Sidebar menu label: {label}")
    ok("frontend static menu keeps Sidebar at L1/L2 and L3 in content metadata")

    combined = "\n".join(read(path) for path in [DOC, REGISTRY, EVIDENCE, VALIDATION, STATIC_MENU, TYPES, APP_LAYOUT])
    for forbidden in FORBIDDEN_TEXT:
        if forbidden in combined:
            fail(f"forbidden label present: {forbidden}")
    lowered = combined.lower()
    for forbidden in FORBIDDEN_EXECUTION:
        if forbidden in lowered:
            fail(f"forbidden execution/import token present: {forbidden}")
    ok("forbidden labels and execution tokens are absent from MENU-GA-R1 scope")

    print(PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
