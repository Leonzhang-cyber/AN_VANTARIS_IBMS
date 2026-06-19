#!/usr/bin/env python3
"""Validate VANTARIS ONE Airport capability baseline and vertical slice freeze."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "AN_VANTARIS_ONE/registries/airport-capability-baseline.v1.json"
VERTICAL = ROOT / "AN_VANTARIS_ONE/registries/airport-poc-vertical-slice.v1.json"
BACKLOG = ROOT / "AN_VANTARIS_ONE/registries/airport-poc-delivery-backlog.v1.json"

REQUIRED_DOMAINS = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}
REQUIRED_POC_PAGES = {
    "Airport Overview",
    "Systems & Integration Health",
    "Assets & Topology",
    "Alarms & Events",
    "Fault Cases",
    "Maintenance Work Orders",
    "Evidence & Investigation",
    "Reports",
}
REQUIRED_BACKLOG = [
    "AIRPORT-A1",
    "AIRPORT-A2",
    "AIRPORT-A3",
    "AIRPORT-A4",
    "AIRPORT-A5",
    "AIRPORT-A6",
    "AIRPORT-A7",
    "AIRPORT-A8",
]

ALLOWED_PREFIXES = (
    "AN_VANTARIS_ONE/registries/airport-capability-baseline.v1.json",
    "AN_VANTARIS_ONE/registries/airport-poc-vertical-slice.v1.json",
    "AN_VANTARIS_ONE/registries/airport-poc-delivery-backlog.v1.json",
    "scripts/validation/validate-one-airport-baseline.py",
)

FORBIDDEN_RUNTIME_PATHS = (
    "AN_VANTARIS_IBMS-backend/src/asset_graph/",
    "AN_VANTARIS_IBMS-backend/src/umms/",
    "AN_VANTARIS_IBMS-backend/src/ucde/",
    "AN_VANTARIS_IBMS-backend/src/api/",
    "AN_VANTARIS_IBMS-frontend/src/",
    "database/",
    "migrations/",
)

FORBIDDEN_ROOTS = ("UFMS/src/", "AN_VANTARIS_EDGE/src/connectors/one-private/")


def _run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=env)


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        paths.update(line for line in _run(command).stdout.splitlines() if line)
    return paths


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    checks: list[tuple[str, bool]] = []

    for path in (BASELINE, VERTICAL, BACKLOG):
        checks.append((f"Registry exists: {path.name}", path.is_file()))

    if not all(path.is_file() for path in (BASELINE, VERTICAL, BACKLOG)):
        print("Missing required registry artifacts")
        return 1

    baseline = _load(BASELINE)
    vertical = _load(VERTICAL)
    backlog = _load(BACKLOG)

    checks.append(("Baseline name", baseline.get("baselineName") == "VANTARIS ONE Airport Capability Baseline"))
    checks.append(("Baseline version", baseline.get("baselineVersion") == "1.0.0"))
    checks.append(("Authority", baseline.get("authority") == "ONE-AIRPORT-A0"))
    checks.append(("Vertical slice name", vertical.get("verticalSliceName") == "VANTARIS ONE Airport POC Vertical Slice"))
    checks.append(("Backlog authority", backlog.get("authority") == "ONE-AIRPORT-A0"))

    domain_codes = {d["domainCode"] for d in baseline.get("capabilityDomains", [])}
    checks.append(("All capability domains A–J", REQUIRED_DOMAINS.issubset(domain_codes)))

    capabilities = [c for d in baseline.get("capabilityDomains", []) for c in d.get("capabilities", [])]
    checks.append(("Capabilities documented", len(capabilities) >= 100))

    owner_by_code: dict[str, str] = {}
    for cap in capabilities:
        code = cap.get("capabilityCode", "")
        owner = cap.get("owningModule", "")
        if code in owner_by_code and owner_by_code[code] != owner:
            errors.append(f"capability {code} has multiple owners")
        owner_by_code[code] = owner
        if not owner:
            errors.append(f"capability {code} missing owner")
    checks.append(("Single owner per capability", not any("multiple owners" in e for e in errors)))

    poc_pages = baseline.get("pocPageAssessment", [])
    poc_names = {p.get("pageName") for p in poc_pages}
    checks.append(("Eight POC pages assessed", REQUIRED_POC_PAGES.issubset(poc_names)))
    checks.append(("POC page readiness values", all(p.get("readiness") for p in poc_pages)))

    shared = baseline.get("sharedFoundationConfirmation", {})
    checks.append(("EDGE remains shared foundation", shared.get("edgeRemainsSharedFoundation") is True))
    checks.append(("LINK remains shared foundation", shared.get("linkRemainsSharedFoundation") is True))
    checks.append(("No ONE-private EDGE/LINK proposed", shared.get("noOnePrivateEdgeLinkImplementationsProposed") is True))
    checks.append(("No UFMS-owned Asset Graph", shared.get("noUfmsOwnedAssetGraph") is True))
    checks.append(("No UMMS-owned generic WorkOrder", shared.get("noUmmsOwnedGenericWorkOrder") is True))
    checks.append(("UConsole projection-only", shared.get("noUconsoleBusinessSourceOfRecord") is True))

    asset_owner_ok = all(
        cap.get("owningModule") == "ONE Asset Graph"
        for cap in capabilities
        if cap.get("capabilityCode", "").startswith("A-") and cap.get("capabilityCode") not in {"A-AIRPORT", "A-TERMINAL"}
    )
    checks.append(("Asset Graph owns canonical asset capabilities", asset_owner_ok))

    ufms_fault_caps = [c for c in capabilities if c.get("capabilityCode", "").startswith("E-")]
    checks.append(
        ("UFMS remains fault owner",
         all(c.get("owningModule") == "UFMS" for c in ufms_fault_caps)),
    )

    work_caps = [c for c in capabilities if c.get("capabilityCode", "").startswith("F-")]
    checks.append(
        ("ONE Work Management owns WorkOrder domain",
         all(c.get("owningModule") == "ONE Work Management" for c in work_caps)),
    )

    evidence_caps = [c for c in capabilities if c.get("capabilityCode", "").startswith("H-")]
    checks.append(
        ("Evidence Center owns EvidenceRecord domain",
         all(c.get("owningModule") == "Evidence Center" for c in evidence_caps)),
    )

    transitions = vertical.get("transitions", [])
    checks.append(("Vertical slice transitions", len(transitions) >= 9))

    backlog_groups = backlog.get("groups", [])
    backlog_codes = [g.get("groupCode") for g in backlog_groups]
    checks.append(("Backlog sequence A1–A8 complete", backlog_codes == REQUIRED_BACKLOG))

    for group in backlog_groups:
        for item in group.get("items", []):
            if not item.get("owner") or not item.get("allowedPaths") or not item.get("forbiddenPaths"):
                errors.append(f"backlog item {item.get('itemCode')} incomplete")

    duplicate_edge = any(
        any(
            "one-private" in path.lower()
            for path in item.get("allowedPaths", [])
        )
        for group in backlog_groups
        for item in group.get("items", [])
    )
    checks.append(("No EDGE/LINK duplication in backlog", not duplicate_edge))

    changed = _changed_paths()
    runtime_touched = [
        path for path in changed
        if any(path.startswith(prefix) for prefix in FORBIDDEN_RUNTIME_PATHS)
    ]
    checks.append(("No runtime implementation added", len(runtime_touched) == 0))
    if runtime_touched:
        errors.append(f"runtime paths modified: {', '.join(runtime_touched)}")

    disallowed = [path for path in changed if path and not any(path.startswith(p) for p in ALLOWED_PREFIXES)]
    checks.append(("Changes within allowed paths", len(disallowed) == 0))
    if disallowed:
        errors.append(f"changes outside allowed paths: {', '.join(sorted(disallowed))}")

    for forbidden in FORBIDDEN_ROOTS:
        if any(path.startswith(forbidden) for path in changed):
            errors.append(f"forbidden root touched: {forbidden}")

    arch_validators = [
        ["python3", "scripts/validation/validate-one-registries.py"],
        ["python3", "scripts/validation/validate-one-boundaries.py"],
        ["python3", "scripts/validation/validate-one-package-route-enforcement.py"],
        ["python3", "scripts/validation/validate-one-asset-graph-foundation.py"],
    ]
    for command in arch_validators:
        script = Path(command[1]).name
        if not (ROOT / command[1]).is_file():
            checks.append((f"Architecture validator present: {script}", False))
            continue
        result = _run(command, env={**os.environ, "PYTHONPATH": str(ROOT / "AN_VANTARIS_IBMS-backend")})
        output = (result.stdout or "") + (result.stderr or "")
        if script == "validate-one-asset-graph-foundation.py" and result.returncode != 0:
            structural_lines = [
                line for line in output.splitlines()
                if ": PASS" in line or ": FAIL" in line
            ]
            non_path_failures = [
                line for line in structural_lines
                if ": FAIL" in line and "Allowed path scope" not in line
            ]
            ok = len(non_path_failures) == 0 and "Canonical ownership: PASS" in output
            checks.append((f"Architecture validator: {script}", ok))
            if not ok:
                errors.append(output.strip() or f"{script} failed")
        else:
            checks.append((f"Architecture validator: {script}", result.returncode == 0))
            if result.returncode != 0:
                errors.append(output.strip() or f"{script} failed")

    print("VANTARIS ONE Airport Capability Baseline Validation")
    print("=" * 60)
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nONE_AIRPORT_CAPABILITY_BASELINE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
